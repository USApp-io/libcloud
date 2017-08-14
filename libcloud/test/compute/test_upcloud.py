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

from libcloud.utils.py3 import httplib
from libcloud.compute.drivers.upcloud import UpcloudDriver
from libcloud.common.types import InvalidCredsError

from libcloud.test import LibcloudTestCase, unittest, MockHttp
from libcloud.test.file_fixtures import ComputeFileFixtures
from libcloud.test.secrets import UPCLOUD_PARAMS


class UpcloudAuthenticationTests(LibcloudTestCase):

    def setUp(self):
        self.driver = UpcloudDriver("nosuchuser", "nopwd")

    def test_authentication_fails(self):
        with self.assertRaises(InvalidCredsError):
            self.driver.list_locations()

class UpcloudDriverTests(LibcloudTestCase):

    def setUp(self):
        UpcloudDriver.connectionCls.conn_class = UpcloudMockHttp
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

class UpcloudMockHttp(MockHttp):
    fixtures = ComputeFileFixtures('upcloud')

    def _1_2_zone(self, method, url, body, headers):
        body = self.fixtures.load('api_1_2_zones.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])



if __name__ == '__main__':
    sys.exit(unittest.main())
