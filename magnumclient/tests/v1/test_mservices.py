#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import testtools
from testtools import matchers

from magnumclient.tests import utils
from magnumclient.v1 import mservices


SERVICE1 = {'id': 123,
            'host': 'fake-host1',
            'binary': 'fake-bin1',
            'state': 'up',
            }
SERVICE2 = {'id': 124,
            'host': 'fake-host2',
            'binary': 'fake-bin2',
            'state': 'down',
            }

fake_responses = {
    '/v1/mservices':
    {
        'GET': (
            {},
            {'mservices': [SERVICE1, SERVICE2]},
        ),
    },
}


class MServiceManagerTest(testtools.TestCase):

    def setUp(self):
        super(MServiceManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = mservices.MServiceManager(self.api)

    def test_coe_service_list(self):
        mservices = self.mgr.list()
        expect = [
            ('GET', '/v1/mservices', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(mservices, matchers.HasLength(2))
