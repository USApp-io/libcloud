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

    def __init__(self, user_id, **kwargs):
        image = kwargs['image']
        size = kwargs['size']
        location = kwargs['location']
        self.body = {
            'server': {
                'title': kwargs['name'],
                'hostname': 'localhost',
                'plan': size.id,
                'zone': location.id,
                'login_user': {'username': user_id,
                               'create_password': 'yes'},
                'storage_devices': {
                    'storage_device': [{
                        'action': 'clone',
                        'title': image.name,
                        'storage': image.id
                    }]
                },
            }
        }

    def to_json(self):
        """Serializes the body to json"""
        return json.dumps(self.body)
