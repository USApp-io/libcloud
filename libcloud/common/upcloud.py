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
import json


class UpcloudCreateNodeRequestBody(object):
    """Body of the create_node request

    Takes the create_node arguments (**kwargs) and constructs the request body
    """
    def __init__(self, user_id, auth=None, **kwargs):
        image = kwargs['image']
        size = kwargs['size']
        location = kwargs['location']
        self.body = {
            'server': {
                'title': kwargs['name'],
                'hostname': 'localhost',
                'plan': size.id,
                'zone': location.id,
                'login_user': _LoginUser(user_id, auth).to_dict(),
                'storage_devices': _StorageDevice(image, size).to_dict()
            }
        }

    def to_json(self):
        """Serializes the body to json"""
        return json.dumps(self.body)


class _LoginUser(object):

    def __init__(self, user_id, auth=None):
        self.user_id = user_id
        self.auth = auth

    def to_dict(self):
        login_user = {'username': self.user_id}
        if self.auth is not None:
            login_user['ssh_keys'] = {
                'ssh_key': [self.auth.pubkey]
            }
        else:
            login_user['create_password'] = 'yes'

        return login_user


class _StorageDevice(object):

    def __init__(self, image, size):
        self.image = image
        self.size = size

    def to_dict(self):
        extra = self.image.extra
        if extra['type'] == 'template':
            return self._storage_device_for_template_image()
        elif extra['type'] == 'cdrom':
            return self._storage_device_for_cdrom_image()

    def _storage_device_for_template_image(self):
        storage_devices = {
            'storage_device': [{
                'action': 'clone',
                'title': self.image.name,
                'storage': self.image.id
            }]
        }
        return storage_devices

    def _storage_device_for_cdrom_image(self):
        storage_devices = {
            'storage_device': [
                {
                    'action': 'create',
                    'title': self.image.name,
                    'size': self.size.disk,
                    'tier': self.size.extra['storage_tier']

                },
                {
                    'action': 'attach',
                    'storage': self.image.id,
                    'type': 'cdrom'
                }
            ]
        }
        return storage_devices
