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

from libcloud.test import LibcloudTestCase, unittest
from libcloud.test.secrets import UPCLOUD_PARAMS
from libcloud.compute.drivers.upcloud import UpcloudDriver


class UpcloudDriverTests(LibcloudTestCase):

    def setUp(self):
        self.driver = UpcloudDriver(*UPCLOUD_PARAMS)

    def test_list_locations(self):
        locations = self.driver.list_locations()
        self.assertTrue(len(locations) >= 1)
        self.assert_location(id='fi-hel1', name='Helsinki #1', country='FI', driver=str(self.driver), locations=locations)

    def assert_location(self, id, name, country, driver, locations):
        """Asserts that location is found in locations"""
        found = False
        for location in locations:
            if location.id == id and \
               location.name == name and \
               location.country == country and \
               location.driver == driver:
               found = True
               break
        self.assertTrue(found, "Location with id {} was not found".format(id))



if __name__ == '__main__':
    sys.exit(unittest.main())
