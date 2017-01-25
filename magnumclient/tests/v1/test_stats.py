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

from magnumclient.tests import utils
from magnumclient.v1 import stats


CLUSTER1 = {'id': 123,
            'uuid': '66666666-7777-8888-9999-000000000001',
            'name': 'cluster1',
            'cluster_template_id': 'e74c40e0-d825-11e2-a28f-0800200c9a61',
            'stack_id': '5d12f6fd-a196-4bf0-ae4c-1f639a523a51',
            'api_address': '172.17.2.1',
            'node_addresses': ['172.17.2.3'],
            'node_count': 2,
            'master_count': 1,
            'project_id': 'abc'
            }
CLUSTER2 = {'id': 124,
            'uuid': '66666666-7777-8888-9999-000000000002',
            'name': 'cluster2',
            'cluster_template_id': 'e74c40e0-d825-11e2-a28f-0800200c9a62',
            'stack_id': '5d12f6fd-a196-4bf0-ae4c-1f639a523a52',
            'api_address': '172.17.2.2',
            'node_addresses': ['172.17.2.4'],
            'node_count': 2,
            'master_count': 1,
            'project_id': 'bcd'
            }


nc = 'node_count'
mc = 'master_count'
C1 = CLUSTER1
C2 = CLUSTER2
fake_responses = {
    '/v1/stats':
    {
        'GET': (
            {},
            {'clusters': 2, 'nodes': C1[nc] + C1[mc] + C2[nc] + C2[mc]},
        )
    },
    '/v1/stats?project_id=%s' % C2['project_id']:
    {
        'GET': (
            {},
            {'clusters': 1, 'nodes': C2[nc] + C2[mc]},
        )
    },
}


class StatsManagerTest(testtools.TestCase):

    def setUp(self):
        super(StatsManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = stats.StatsManager(self.api)

    def test_stats(self):
        stats = self.mgr.list()
        expect = [
            ('GET', '/v1/stats', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        expected_stats = {'clusters': 2,
                          'nodes': C1[nc] + C1[mc] + C2[nc] + C2[mc]}
        self.assertEqual(expected_stats, stats._info)

    def test_stats_with_project_id(self):
        expect = [
            ('GET', '/v1/stats?project_id=%s' % CLUSTER2['project_id'], {},
             None),
        ]
        stats = self.mgr.list(project_id=CLUSTER2['project_id'])
        self.assertEqual(expect, self.api.calls)
        expected_stats = {'clusters': 1,
                          'nodes': C2[nc] + C2[mc]}
        self.assertEqual(expected_stats, stats._info)
