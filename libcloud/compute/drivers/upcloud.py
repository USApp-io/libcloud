# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Upcloud node driver
"""
import base64

from libcloud.utils.py3 import httplib
from libcloud.compute.base import NodeDriver, NodeLocation, NodeSize
from libcloud.compute.base import NodeImage
from libcloud.compute.types import Provider
from libcloud.common.base import ConnectionUserAndKey, JsonResponse
from libcloud.common.types import InvalidCredsError


class UpcloudResponse(JsonResponse):
    """Response class for UpcloudDriver"""

    def parse_error(self):
        data = self.parse_body()
        if self.status == httplib.UNAUTHORIZED:
            raise InvalidCredsError(value=data['error']['error_message'])


class UpcloudConnection(ConnectionUserAndKey):
    """Connection class for UpcloudDriver"""
    host = 'api.upcloud.com'
    responseCls = UpcloudResponse

    def add_default_headers(self, headers):
        """Adds headers that are needed for all requests"""
        headers['Authorization'] = self._basic_auth()
        headers['Accept'] = 'application/json'
        return headers

    def _basic_auth(self):
        """Constructs basic auth header content string"""
        credentials = bytes("{}:{}".format(self.user_id, self.key), 'utf-8')
        credentials = base64.b64encode(credentials)
        return 'Basic {}'.format(credentials.decode('ascii'))


class UpcloudDriver(NodeDriver):
    """Upcloud node driver

    :keyword    username: Username required for authentication
    :type       username: ``str``

    :keyword    password: Password required for authentication
    :type       password: ``str``
    """
    type = Provider.UPCLOUD
    name = 'Upcloud'
    website = 'https://www.upcloud.com'
    connectionCls = UpcloudConnection

    def __init__(self, username, password, **kwargs):
        super(UpcloudDriver, self).__init__(key=username, secret=password,
                                            **kwargs)

    def list_locations(self):
        """List of locations where nodes can be"""
        response = self.connection.request('1.2/zone')
        return self._to_node_locations(response.object['zones']['zone'])

    def list_sizes(self):
        """List node sizes
        ``NodeSize`` has extra fields ``core_number``and ``storage_tier``
        """
        response = self.connection.request('1.2/plan')
        return self._to_node_sizes(response.object['plans']['plan'])

    def list_images(self):
        """Lists images from upcloud from two different places
        and joins them to one"""
        response = self.connection.request('1.2/storage/template')
        obj = response.object
        response = self.connection.request('1.2/storage/cdrom')
        obj['storages']['storage'].extend(response.object['storages']['storage'])
        return self._to_node_images(obj['storages']['storage'])

    def _to_node_locations(self, zones):
        return [self._construct_node_location(zone) for zone in zones]

    def _construct_node_location(self, zone):
        return NodeLocation(id=zone['id'],
                            name=zone['description'],
                            country=self._parse_country(zone['id']),
                            driver=str(self))

    def _parse_country(self, zone_id):
        """Parses the country information out of zone_id.
        Zone_id format [country]_[city][number], like fi_hel1"""
        return zone_id.split('-')[0].upper()

    def _to_node_sizes(self, plans):
        return [self._construct_node_size(plan) for plan in plans]

    def _construct_node_size(self, plan):
        extra = self._copy_dict(('core_number', 'storage_tier'), plan)
        return NodeSize(id=plan['name'], name=plan['name'],
                        ram=plan['memory_amount'],
                        disk=plan['storage_size'],
                        bandwidth=plan['public_traffic_out'],
                        price=None, driver=str(self),
                        extra=extra)

    def _to_node_images(self, images):
        return [self._construct_node_image(image) for image in images]

    def _construct_node_image(self, image):
        extra = self._copy_dict(('access', 'license',
                                 'size', 'state', 'type'), image)
        return NodeImage(id=image['uuid'],
                         name=image['title'],
                         driver=str(self),
                         extra=extra)

    def _copy_dict(self, keys, d):
        extra = {}
        for key in keys:
            extra[key] = d[key]
        return extra
