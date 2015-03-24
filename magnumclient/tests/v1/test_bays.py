# Copyright 2015 IBM Corp.
#
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
from magnumclient.v1 import bays


BAY1 = {'id': 123,
        'uuid': '66666666-7777-8888-9999-000000000001',
        'name': 'bay1',
        'baymodel_id': 'e74c40e0-d825-11e2-a28f-0800200c9a61',
        'stack_id': '5d12f6fd-a196-4bf0-ae4c-1f639a523a51',
        'api_address': '172.17.2.1',
        'node_addresses': ['172.17.2.3'],
        'node_count': 2,
        }
BAY2 = {'id': 124,
        'uuid': '66666666-7777-8888-9999-000000000002',
        'name': 'bay2',
        'baymodel_id': 'e74c40e0-d825-11e2-a28f-0800200c9a62',
        'stack_id': '5d12f6fd-a196-4bf0-ae4c-1f639a523a52',
        'api_address': '172.17.2.2',
        'node_addresses': ['172.17.2.4'],
        'node_count': 2,
        }

CREATE_BAY = copy.deepcopy(BAY1)
del CREATE_BAY['id']
del CREATE_BAY['uuid']
del CREATE_BAY['stack_id']
del CREATE_BAY['api_address']
del CREATE_BAY['node_addresses']

UPDATED_BAY = copy.deepcopy(BAY1)
NEW_NAME = 'newbay'
UPDATED_BAY['name'] = NEW_NAME

fake_responses = {
    '/v1/bays':
    {
        'GET': (
            {},
            {'bays': [BAY1, BAY2]},
        ),
        'POST': (
            {},
            CREATE_BAY,
        ),
    },
    '/v1/bays/%s' % BAY1['id']:
    {
        'GET': (
            {},
            BAY1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_BAY,
        ),
    },
    '/v1/bays/%s' % BAY1['name']:
    {
        'GET': (
            {},
            BAY1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_BAY,
        ),
    },
}


class BayManagerTest(testtools.TestCase):

    def setUp(self):
        super(BayManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = bays.BayManager(self.api)

    def test_bay_list(self):
        bays = self.mgr.list()
        expect = [
            ('GET', '/v1/bays', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(bays, matchers.HasLength(2))

    def test_bay_show_by_id(self):
        bay = self.mgr.get(BAY1['id'])
        expect = [
            ('GET', '/v1/bays/%s' % BAY1['id'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(BAY1['name'], bay.name)
        self.assertEqual(BAY1['baymodel_id'], bay.baymodel_id)

    def test_bay_show_by_name(self):
        bay = self.mgr.get(BAY1['name'])
        expect = [
            ('GET', '/v1/bays/%s' % BAY1['name'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(BAY1['name'], bay.name)
        self.assertEqual(BAY1['baymodel_id'], bay.baymodel_id)

    def test_bay_create(self):
        bay = self.mgr.create(**CREATE_BAY)
        expect = [
            ('POST', '/v1/bays', {}, CREATE_BAY),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(bay)

    def test_bay_delete_by_id(self):
        bay = self.mgr.delete(BAY1['id'])
        expect = [
            ('DELETE', '/v1/bays/%s' % BAY1['id'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(bay)

    def test_bay_delete_by_name(self):
        bay = self.mgr.delete(BAY1['name'])
        expect = [
            ('DELETE', '/v1/bays/%s' % BAY1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(bay)

    def test_bay_update(self):
        patch = {'op': 'replace',
                 'value': NEW_NAME,
                 'path': '/name'}
        bay = self.mgr.update(id=BAY1['id'], patch=patch)
        expect = [
            ('PATCH', '/v1/bays/%s' % BAY1['id'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_NAME, bay.name)
