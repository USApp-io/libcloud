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
from libcloud.compute.drivers.upcloud import UpcloudResponse

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
        #UpcloudDriver.connectionCls.conn_class = UpcloudMockHttp
        #UpcloudDriver.connectionCls.responseCls = UpcloudPersistResponse
        self.driver = UpcloudDriver(*UPCLOUD_PARAMS)

    def test_list_locations(self):
        locations = self.driver.list_locations()
        self.assertTrue(len(locations) >= 1)
        self.assert_location(id='fi-hel1', name='Helsinki #1', country='FI', driver=str(self.driver), locations=locations)

    def test_list_sizes(self):
        sizes = self.driver.list_sizes()
        self.assertTrue(len(sizes) >= 1)
        self.assert_size(id='1xCPU-1GB',
                         name='1xCPU-1GB',
                         ram=1024,
                         disk=30,
                         bandwidth=2048,
                         price=None,
                         driver=str(self.driver),
                         extra_core_number=1,
                         extra_storage_tier='maxiops',
                         sizes=sizes)

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

    def assert_size(self, id, name, ram, disk, bandwidth, price,
                    driver, extra_core_number, extra_storage_tier,
                    sizes):
        """Assert size data is found in sizes"""
        found = False
        for size in sizes:
            if size.id == id and \
               size.name == name and \
               size.ram == ram and \
               size.disk == disk and \
               size.bandwidth == bandwidth and \
               size.price == price and \
               size.driver == driver and \
               size.extra['core_number'] == extra_core_number and \
               size.extra['storage_tier'] == extra_storage_tier:
                found = True
                break
        self.assertTrue(found, "Size with id {} was not found".format(id))


class UpcloudMockHttp(MockHttp):
    fixtures = ComputeFileFixtures('upcloud')

    def _1_2_zone(self, method, url, body, headers):
        body = self.fixtures.load('api_1_2_zone.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

if __name__ == '__main__':
    sys.exit(unittest.main())
