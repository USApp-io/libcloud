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
import sys
import json

from libcloud.common.upcloud import UpcloudCreateNodeRequestBody
from libcloud.compute.base import NodeImage, NodeSize, NodeLocation
from libcloud.test import unittest


class TestUpcloudCreateNodeRequestBody(unittest.TestCase):

    def test_creating_node_from_template_image(self):
        image = NodeImage(id='01000000-0000-4000-8000-000030060200',
                          name='Ubuntu Server 16.04 LTS (Xenial Xerus)',
                          driver='',
                          extra={'type': 'template'})
        location = NodeLocation(id='fi-hel1', name='Helsinki #1', country='FI', driver='')
        size = NodeSize(id='1xCPU-1GB', name='1xCPU-1GB', ram=1024, disk=30, bandwidth=2048,
                        extra={'core_number': 1, 'storage_tier': 'maxiops'}, price=None, driver='')

        body = UpcloudCreateNodeRequestBody(user_id='somename', name='ts', image=image, location=location, size=size)
        json_body = body.to_json()
        dict_body = json.loads(json_body)
        expected_body = {
            'server': {
                'title': 'ts',
                'hostname': 'localhost',
                'plan': '1xCPU-1GB',
                'zone': 'fi-hel1',
                'login_user': {'username': 'somename',
                               'create_password': 'yes'},
                'storage_devices': {
                    'storage_device': [{
                        'action': 'clone',
                        'title': 'Ubuntu Server 16.04 LTS (Xenial Xerus)',
                        'storage': '01000000-0000-4000-8000-000030060200'
                    }]
                },
            }
        }
        self.assertDictEqual(expected_body, dict_body)

if __name__ == '__main__':
    sys.exit(unittest.main())
