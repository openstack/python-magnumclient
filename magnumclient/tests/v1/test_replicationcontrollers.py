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
from magnumclient.v1 import replicationcontrollers as rcs


RC1 = {'id': 123,
       'uuid': '66666666-7777-8888-9999-000000000001',
       'name': 'rc1',
       'images': ['image1'],
       'bay_uuid': '5d12f6fd-a196-4bf0-ae4c-1f639a523a51',
       'selector': {'name': 'bar1'},
       'replicas': 1
       }
RC2 = {'id': 124,
       'uuid': '66666666-7777-8888-9999-000000000002',
       'name': 'rc2',
       'images': ['image2'],
       'bay_uuid': '5d12f6fd-a196-4bf0-ae4c-1f639a523a52',
       'selector': {'name': 'bar2'},
       'replicas': 2
       }
CREATE_RC = {'manifest_url': 'file:///a/b.json'}
UPDATED_RC = copy.deepcopy(RC1)
NEW_REPLICAS = 3
UPDATED_RC['replicas'] = NEW_REPLICAS

fake_responses = {
    '/v1/rcs':
    {
        'GET': (
            {},
            {'rcs': [RC1, RC2]},
        ),
        'POST': (
            {},
            CREATE_RC,
        ),
    },
    '/v1/rcs/?bay_ident=%s' % (RC1['bay_uuid']):
    {
        'GET': (
            {},
            {'rcs': [RC1, RC2]},
        ),
    },
    '/v1/rcs/%s/?bay_ident=%s' % (RC1['id'], RC1['bay_uuid']):
    {
        'GET': (
            {},
            RC1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_RC,
        ),
    },
    '/v1/rcs/%s/?bay_ident=%s' % (RC1['name'], RC1['bay_uuid']):
    {
        'GET': (
            {},
            RC1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_RC,
        ),
    },
}


class RCManagerTest(testtools.TestCase):

    def setUp(self):
        super(RCManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = rcs.ReplicationControllerManager(self.api)

    def test_rc_list(self):
        rcs = self.mgr.list(RC1['bay_uuid'])
        expect = [
            ('GET', '/v1/rcs/?bay_ident=%s' % (RC1['bay_uuid']), {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(rcs, matchers.HasLength(2))

    def test_rc_show_by_id(self):
        rc = self.mgr.get(RC1['id'], RC1['bay_uuid'])
        expect = [
            ('GET', '/v1/rcs/%s/?bay_ident=%s' % (RC1['id'],
                                                  RC1['bay_uuid']), {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(RC1['name'], rc.name)
        self.assertEqual(RC1['bay_uuid'], rc.bay_uuid)
        self.assertEqual(RC1['replicas'], rc.replicas)

    def test_rc_show_by_name(self):
        rc = self.mgr.get(RC1['name'], RC1['bay_uuid'])
        expect = [
            ('GET', '/v1/rcs/%s/?bay_ident=%s' % (RC1['name'],
                                                  RC1['bay_uuid']), {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(RC1['name'], rc.name)
        self.assertEqual(RC1['bay_uuid'], rc.bay_uuid)
        self.assertEqual(RC1['replicas'], rc.replicas)

    def test_rc_create(self):
        rc = self.mgr.create(**CREATE_RC)
        expect = [
            ('POST', '/v1/rcs', {}, CREATE_RC),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(rc)

    def test_rc_create_fail(self):
        CREATE_RC_FAIL = copy.deepcopy(CREATE_RC)
        CREATE_RC_FAIL["wrong_key"] = "wrong"
        self.assertRaisesRegexp(exceptions.InvalidAttribute,
                                ("Key must be in %s" %
                                 ','.join(rcs.CREATION_ATTRIBUTES)),
                                self.mgr.create, **CREATE_RC_FAIL)
        self.assertEqual([], self.api.calls)

    def test_rc_delete_by_id(self):
        rc = self.mgr.delete(RC1['id'], RC1['bay_uuid'])
        expect = [
            ('DELETE', '/v1/rcs/%s/?bay_ident=%s' % (RC1['id'],
                                                     RC1['bay_uuid']),
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(rc)

    def test_rc_delete_by_name(self):
        rc = self.mgr.delete(RC1['name'], RC1['bay_uuid'])
        expect = [
            ('DELETE', '/v1/rcs/%s/?bay_ident=%s' % (RC1['name'],
                                                     RC1['bay_uuid']),
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(rc)

    def test_rc_update(self):
        patch = {'op': 'replace',
                 'value': NEW_REPLICAS,
                 'path': '/replicas'}
        rc = self.mgr.update(id=RC1['id'],
                             bay_ident=RC1['bay_uuid'],
                             patch=patch)
        expect = [
            ('PATCH', '/v1/rcs/%s/?bay_ident=%s' % (RC1['id'],
                                                    RC1['bay_uuid']), {},
             patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_REPLICAS, rc.replicas)
