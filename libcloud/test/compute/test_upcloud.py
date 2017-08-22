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

from __future__ import with_statement
import sys
import re
import json

from libcloud.utils.py3 import httplib
from libcloud.compute.drivers.upcloud import UpcloudDriver
from libcloud.common.types import InvalidCredsError
from libcloud.compute.drivers.upcloud import UpcloudResponse
from libcloud.compute.types import NodeState
from libcloud.compute.base import NodeImage, NodeSize, NodeLocation, NodeAuthSSHKey
from libcloud.test import LibcloudTestCase, unittest, MockHttp
from libcloud.test.file_fixtures import ComputeFileFixtures
from libcloud.test.secrets import UPCLOUD_PARAMS


class UpcloudPersistResponse(UpcloudResponse):

    def parse_body(self):
        import os
        path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'compute', 'fixtures', 'upcloud'))
        filename = 'api' + self.request.path_url.replace('/', '_').replace('.', '_') + '.json'
        filename = os.path.join(path, filename)
        if not os.path.exists(filename):
            with open(filename, 'w+') as f:
                f.write(self.body)
        return super(UpcloudPersistResponse, self).parse_body()


class UpcloudAuthenticationTests(LibcloudTestCase):

    def setUp(self):
        self.driver = UpcloudDriver("nosuchuser", "nopwd")

    def test_authentication_fails(self):
        with self.assertRaises(InvalidCredsError):
            self.driver.list_locations()


class UpcloudDriverTests(LibcloudTestCase):

    def setUp(self):
        UpcloudDriver.connectionCls.conn_class = UpcloudMockHttp
        # UpcloudDriver.connectionCls.responseCls = UpcloudPersistResponse
        self.driver = UpcloudDriver(*UPCLOUD_PARAMS)

    def test_list_locations(self):
        locations = self.driver.list_locations()
        self.assertTrue(len(locations) >= 1)
        expected_node_location = NodeLocation(id='fi-hel1',
                                              name='Helsinki #1',
                                              country='FI',
                                              driver=str(self.driver))
        self.assert_object(expected_node_location, objects=locations)

    def test_list_sizes(self):
        sizes = self.driver.list_sizes()
        self.assertTrue(len(sizes) >= 1)
        expected_node_size = NodeSize(id='1xCPU-1GB',
                                      name='1xCPU-1GB',
                                      ram=1024,
                                      disk=30,
                                      bandwidth=2048,
                                      price=None,
                                      driver=str(self.driver),
                                      extra={'core_number': 1,
                                             'storage_tier': 'maxiops'})
        self.assert_object(expected_node_size, objects=sizes)

    def test_list_images(self):
        images = self.driver.list_images()
        self.assertTrue(len(images) >= 1)
        expected_node_image = NodeImage(id='01000000-0000-4000-8000-000010010101',
                                        name='Windows Server 2003 R2 Standard (CD 1)',
                                        driver=str(self.driver),
                                        extra={'access': 'public',
                                               'licence': 0,
                                               'size': 1,
                                               'state': 'online',
                                               'type': 'cdrom'})
        self.assert_object(expected_node_image, objects=images)

    def test_create_node_from_template(self):
        image = NodeImage(id='01000000-0000-4000-8000-000030060200',
                          name='Ubuntu Server 16.04 LTS (Xenial Xerus)',
                          extra={'type': 'template'},
                          driver=self.driver)
        location = NodeLocation(id='fi-hel1', name='Helsinki #1', country='FI', driver=self.driver)
        size = NodeSize(id='1xCPU-1GB', name='1xCPU-1GB', ram=1024, disk=30, bandwidth=2048,
                        extra={'core_number': 1, 'storage_tier': 'maxiops'}, price=None, driver=self.driver)
        node = self.driver.create_node(name='test_server', size=size, image=image, location=location)

        self.assertTrue(re.match('^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$', node.id))
        self.assertEquals(node.name, 'test_server')
        self.assertEquals(node.state, NodeState.STARTING)
        self.assertTrue(len(node.public_ips) > 0)
        self.assertTrue(len(node.private_ips) > 0)
        self.assertEquals(node.driver, self.driver)
        self.assertTrue(len(node.extra['password']) > 0)
        self.assertTrue(len(node.extra['vnc_password']) > 0)

    def test_create_node_with_ssh_keys(self):
        image = NodeImage(id='01000000-0000-4000-8000-000030060200',
                          name='Ubuntu Server 16.04 LTS (Xenial Xerus)',
                          extra={'type': 'template'},
                          driver=self.driver)
        location = NodeLocation(id='fi-hel1', name='Helsinki #1', country='FI', driver=self.driver)
        size = NodeSize(id='1xCPU-1GB', name='1xCPU-1GB', ram=1024, disk=30, bandwidth=2048,
                        extra={'core_number': 1, 'storage_tier': 'maxiops'}, price=None, driver=self.driver)

        auth = NodeAuthSSHKey('ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDCUUFfYA+T+BzoM7IIR' +
                              'VXNndDjYvIROMjfyRBhhHf6RZd1IkAwcWSGISePh2tIiqu8gJalYYHg2w' +
                              'i3ofMJfi6VYeyBFWrIDhMK0v+ziBbBUtlJNnP6MBOR/13avkk+76TVrcG' +
                              'xu49RaptYNzZ21XluvIlaqqdjAhoh0J+o7OZTKD7N1UTPL7CIX+ITaA+g' +
                              '3FR5ITClk8KmIbp3vT6fUPD7pNUrGBZTpcPcHq8rodQ8igWIVdSkb9iky' +
                              'ew4y6wvsubQ3Ykn26XeKxrk1vA6ZKMHt7ijCYmfL0LcDfctNymy/vc6hs' +
                              'WxCRS5OqNQ6nxdXpv9A+TD0sJuf5jaoH7MSpU1 mika.lackman@gmail.com')
        node = self.driver.create_node(name='test_server', size=size, image=image, location=location, auth=auth)
        self.assertTrue(re.match('^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$', node.id))
        self.assertEquals(node.name, 'test_server')
        self.assertEquals(node.state, NodeState.STARTING)
        self.assertTrue(len(node.public_ips) > 0)
        self.assertTrue(len(node.private_ips) > 0)
        self.assertEquals(node.driver, self.driver)

    def assert_object(self, expected_object, objects):
        same_data = any([self.objects_equals(expected_object, obj) for obj in objects])
        self.assertTrue(same_data, "Objects does not match")

    def objects_equals(self, expected_obj, obj):
        for name in vars(expected_obj):
            expected_data = getattr(expected_obj, name)
            actual_data = getattr(obj, name)
            same_data = self.data_equals(expected_data, actual_data)
            if not same_data:
                break
        return same_data

    def data_equals(self, expected_data, actual_data):
        if isinstance(expected_data, dict):
            return self.dicts_equals(expected_data, actual_data)
        else:
            return expected_data == actual_data

    def dicts_equals(self, d1, d2):
        """Assumes dicts to contain only hashable types"""
        return set(d1.values()) == set(d2.values())


class UpcloudMockHttp(MockHttp):
    fixtures = ComputeFileFixtures('upcloud')

    def _1_2_zone(self, method, url, body, headers):
        body = self.fixtures.load('api_1_2_zone.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _1_2_plan(self, method, url, body, headers):
        body = self.fixtures.load('api_1_2_plan.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _1_2_storage_cdrom(self, method, url, body, headers):
        body = self.fixtures.load('api_1_2_storage_cdrom.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _1_2_storage_template(self, method, url, body, headers):
        body = self.fixtures.load('api_1_2_storage_template.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _1_2_server(self, method, url, body, headers):
        dbody = json.loads(body)
        storages = dbody['server']['storage_devices']['storage_device']
        if any(['type' in storage and storage['type'] == 'cdrom' for storage in storages]):
            body = self.fixtures.load('api_1_2_server_from_cdrom.json')
        else:
            body = self.fixtures.load('api_1_2_server_from_template.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

if __name__ == '__main__':
    sys.exit(unittest.main())
