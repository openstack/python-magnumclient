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

import copy

import testtools
from testtools import matchers

from magnumclient.tests import utils
from magnumclient.v1 import quotas


QUOTA1 = {
    'id': 123,
    'resource': "Cluster",
    'hard_limit': 5,
    'project_id': 'abc'
}

QUOTA2 = {
    'id': 124,
    'resource': "Cluster",
    'hard_limit': 10,
    'project_id': 'bcd'
}

CREATE_QUOTA = copy.deepcopy(QUOTA1)
del CREATE_QUOTA['id']

UPDATED_QUOTA = copy.deepcopy(QUOTA2)
NEW_HARD_LIMIT = 20
UPDATED_QUOTA['hard_limit'] = NEW_HARD_LIMIT

fake_responses = {
    '/v1/quotas?all_tenants=True':
    {
        'GET': (
            {},
            {'quotas': [QUOTA1, QUOTA2]},
        ),
    },
    '/v1/quotas':
    {
        'GET': (
            {},
            {'quotas': [QUOTA1]},
        ),
        'POST': (
            {},
            QUOTA1,
        ),
    },
    '/v1/quotas/%(id)s/%(res)s' % {'id': QUOTA2['project_id'],
                                   'res': QUOTA2['resource']}:
    {
        'GET': (
            {},
            QUOTA2,
        ),
        'PATCH': (
            {},
            UPDATED_QUOTA,
        ),
        'DELETE': (
            {},
            None,
        ),
    },
}


class QuotasManagerTest(testtools.TestCase):

    def setUp(self):
        super(QuotasManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = quotas.QuotasManager(self.api)

    def test_list_quotas(self):
        quotas = self.mgr.list()
        expect = [
            ('GET', '/v1/quotas', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(quotas, matchers.HasLength(1))

    def test_list_quotas_all(self):
        quotas = self.mgr.list(all_tenants=True)
        expect = [
            ('GET', '/v1/quotas?all_tenants=True', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(quotas, matchers.HasLength(2))

    def test_show_project_resource_quota(self):
        expect = [
            ('GET',
             '/v1/quotas/%(id)s/%(res)s' % {'id': QUOTA2['project_id'],
                                            'res': QUOTA2['resource']},
             {},
             None),
        ]
        quotas = self.mgr.get(QUOTA2['project_id'], QUOTA2['resource'])
        self.assertEqual(expect, self.api.calls)
        expected_quotas = QUOTA2
        self.assertEqual(expected_quotas, quotas._info)

    def test_quota_create(self):
        quota = self.mgr.create(**CREATE_QUOTA)
        expect = [
            ('POST', '/v1/quotas', {}, CREATE_QUOTA),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(QUOTA1, quota._info)

    def test_quota_update(self):
        patch = {
            'resource': "Cluster",
            'hard_limit': NEW_HARD_LIMIT,
            'project_id': 'bcd'
        }
        quota = self.mgr.update(id=QUOTA2['project_id'],
                                resource=QUOTA2['resource'],
                                patch=patch)
        expect = [
            ('PATCH', '/v1/quotas/%(id)s/%(res)s' % {
                'id': QUOTA2['project_id'],
                'res': QUOTA2['resource']}, {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_HARD_LIMIT, quota.hard_limit)

    def test_quota_delete(self):
        quota = self.mgr.delete(QUOTA2['project_id'], QUOTA2['resource'])
        expect = [
            ('DELETE',
             '/v1/quotas/%(id)s/%(res)s' % {'id': QUOTA2['project_id'],
                                            'res': QUOTA2['resource']},
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(quota)
