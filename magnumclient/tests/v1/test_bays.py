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

from magnumclient import exceptions
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
        'master_count': 1,
        }
BAY2 = {'id': 124,
        'uuid': '66666666-7777-8888-9999-000000000002',
        'name': 'bay2',
        'baymodel_id': 'e74c40e0-d825-11e2-a28f-0800200c9a62',
        'stack_id': '5d12f6fd-a196-4bf0-ae4c-1f639a523a52',
        'api_address': '172.17.2.2',
        'node_addresses': ['172.17.2.4'],
        'node_count': 2,
        'master_count': 1,
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
    '/v1/bays/%s/?rollback=True' % BAY1['id']:
        {
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
    '/v1/bays/?limit=2':
    {
        'GET': (
            {},
            {'bays': [BAY1, BAY2]},
        ),
    },
    '/v1/bays/?marker=%s' % BAY2['uuid']:
    {
        'GET': (
            {},
            {'bays': [BAY1, BAY2]},
        ),
    },
    '/v1/bays/?limit=2&marker=%s' % BAY2['uuid']:
    {
        'GET': (
            {},
            {'bays': [BAY1, BAY2]},
        ),
    },
    '/v1/bays/?sort_dir=asc':
    {
        'GET': (
            {},
            {'bays': [BAY1, BAY2]},
        ),
    },
    '/v1/bays/?sort_key=uuid':
    {
        'GET': (
            {},
            {'bays': [BAY1, BAY2]},
        ),
    },
    '/v1/bays/?sort_key=uuid&sort_dir=desc':
    {
        'GET': (
            {},
            {'bays': [BAY2, BAY1]},
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

    def _test_bay_list_with_filters(self, limit=None, marker=None,
                                    sort_key=None, sort_dir=None,
                                    detail=False, expect=[]):
        bays_filter = self.mgr.list(limit=limit, marker=marker,
                                    sort_key=sort_key,
                                    sort_dir=sort_dir,
                                    detail=detail)
        self.assertEqual(expect, self.api.calls)
        self.assertThat(bays_filter, matchers.HasLength(2))

    def test_bay_list_with_limit(self):
        expect = [
            ('GET', '/v1/bays/?limit=2', {}, None),
        ]
        self._test_bay_list_with_filters(
            limit=2,
            expect=expect)

    def test_bay_list_with_marker(self):
        expect = [
            ('GET', '/v1/bays/?marker=%s' % BAY2['uuid'], {}, None),
        ]
        self._test_bay_list_with_filters(
            marker=BAY2['uuid'],
            expect=expect)

    def test_bay_list_with_marker_limit(self):
        expect = [
            ('GET', '/v1/bays/?limit=2&marker=%s' % BAY2['uuid'], {}, None),
        ]
        self._test_bay_list_with_filters(
            limit=2, marker=BAY2['uuid'],
            expect=expect)

    def test_bay_list_with_sort_dir(self):
        expect = [
            ('GET', '/v1/bays/?sort_dir=asc', {}, None),
        ]
        self._test_bay_list_with_filters(
            sort_dir='asc',
            expect=expect)

    def test_bay_list_with_sort_key(self):
        expect = [
            ('GET', '/v1/bays/?sort_key=uuid', {}, None),
        ]
        self._test_bay_list_with_filters(
            sort_key='uuid',
            expect=expect)

    def test_bay_list_with_sort_key_dir(self):
        expect = [
            ('GET', '/v1/bays/?sort_key=uuid&sort_dir=desc', {}, None),
        ]
        self._test_bay_list_with_filters(
            sort_key='uuid', sort_dir='desc',
            expect=expect)

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

    def test_bay_create_with_discovery_url(self):
        bay_with_discovery = dict()
        bay_with_discovery.update(CREATE_BAY)
        bay_with_discovery['discovery_url'] = 'discovery_url'
        bay = self.mgr.create(**bay_with_discovery)
        expect = [
            ('POST', '/v1/bays', {}, bay_with_discovery),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(bay)

    def test_bay_create_with_bay_create_timeout(self):
        bay_with_timeout = dict()
        bay_with_timeout.update(CREATE_BAY)
        bay_with_timeout['bay_create_timeout'] = '15'
        bay = self.mgr.create(**bay_with_timeout)
        expect = [
            ('POST', '/v1/bays', {}, bay_with_timeout),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(bay)

    def test_bay_create_fail(self):
        CREATE_BAY_FAIL = copy.deepcopy(CREATE_BAY)
        CREATE_BAY_FAIL["wrong_key"] = "wrong"
        self.assertRaisesRegex(exceptions.InvalidAttribute,
                               ("Key must be in %s" %
                                ','.join(bays.CREATION_ATTRIBUTES)),
                               self.mgr.create, **CREATE_BAY_FAIL)
        self.assertEqual([], self.api.calls)

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

    def test_bay_update_with_rollback(self):
        patch = {'op': 'replace',
                 'value': NEW_NAME,
                 'path': '/name'}
        bay = self.mgr.update(id=BAY1['id'], patch=patch, rollback=True)
        expect = [
            ('PATCH', '/v1/bays/%s/?rollback=True' % BAY1['id'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_NAME, bay.name)
