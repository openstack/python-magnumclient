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
from magnumclient.v1 import nodes


NODE1 = {'id': 123,
         'uuid': '66666666-7777-8888-9999-000000000001',
         'type': 'virt',
         'image_id': 'ubuntu',
         'ironic_node_id': '5d12f6fd-a196-4bf0-ae4c-1f639a523a51',
         }
NODE2 = {'id': 124,
         'uuid': '66666666-7777-8888-9999-000000000002',
         'type': 'ironic',
         'image_id': 'rhel7',
         'ironic_node_id': '5d12f6fd-a196-4bf0-ae4c-1f639a523a52',
         }

CREATE_NODE = copy.deepcopy(NODE1)
del CREATE_NODE['id']
del CREATE_NODE['uuid']
del CREATE_NODE['ironic_node_id']

UPDATED_NODE = copy.deepcopy(NODE1)
NEW_IMAGE_ID = 'centos7'
UPDATED_NODE['image_id'] = NEW_IMAGE_ID

fake_responses = {
    '/v1/nodes':
    {
        'GET': (
            {},
            {'nodes': [NODE1, NODE2]},
        ),
        'POST': (
            {},
            CREATE_NODE,
        ),
    },
    '/v1/nodes/%s' % NODE1['id']:
    {
        'GET': (
            {},
            NODE1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_NODE,
        ),
    },
}


class NodeManagerTest(testtools.TestCase):

    def setUp(self):
        super(NodeManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = nodes.NodeManager(self.api)

    def test_node_list(self):
        nodes = self.mgr.list()
        expect = [
            ('GET', '/v1/nodes', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, matchers.HasLength(2))

    def test_node_show(self):
        node = self.mgr.get(NODE1['id'])
        expect = [
            ('GET', '/v1/nodes/%s' % NODE1['id'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NODE1['type'], node.type)
        self.assertEqual(NODE1['image_id'], node.image_id)

    def test_node_create(self):
        node = self.mgr.create(**CREATE_NODE)
        expect = [
            ('POST', '/v1/nodes', {}, CREATE_NODE),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(node)

    def test_node_create_fail(self):
        CREATE_NODE_FAIL = copy.deepcopy(CREATE_NODE)
        CREATE_NODE_FAIL["wrong_key"] = "wrong"
        self.assertRaisesRegexp(exceptions.InvalidAttribute,
                                ("Key must be in %s" %
                                 ','.join(nodes.CREATION_ATTRIBUTES)),
                                self.mgr.create, **CREATE_NODE_FAIL)
        self.assertEqual([], self.api.calls)

    def test_node_delete(self):
        node = self.mgr.delete(NODE1['id'])
        expect = [
            ('DELETE', '/v1/nodes/%s' % NODE1['id'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(node)

    def test_node_update(self):
        patch = {'op': 'replace',
                 'value': NEW_IMAGE_ID,
                 'path': '/image_id'}
        node = self.mgr.update(id=NODE1['id'], patch=patch)
        expect = [
            ('PATCH', '/v1/nodes/%s' % NODE1['id'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_IMAGE_ID, node.image_id)
