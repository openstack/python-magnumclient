# Copyright (c) 2018 European Organization for Nuclear Research.
# All Rights Reserved.
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

import testtools
from testtools import matchers

from magnumclient.tests import utils
from magnumclient.v1 import nodegroups


NODEGROUP1 = {
    'id': 123,
    'uuid': '66666666-7777-8888-9999-000000000001',
    'cluster_id': '66666666-7777-8888-9999-000000000000',
    'name': 'test-worker',
    'node_addresses': ['172.17.2.3'],
    'node_count': 2,
    'project_id': 'fake_project',
    'labels': {},
    'flavor_id': 'fake_flavor_1',
    'image_id': 'fake_image',
    'is_default': True,
    'role': 'worker',
    'max_node_count': 10,
    'min_node_count': 1
}
NODEGROUP2 = {
    'id': 124,
    'uuid': '66666666-7777-8888-9999-000000000002',
    'cluster_id': '66666666-7777-8888-9999-000000000000',
    'name': 'test-master',
    'node_addresses': ['172.17.2.4'],
    'node_count': 2,
    'project_id': 'fake_project',
    'labels': {},
    'flavor_id': 'fake_flavor_1',
    'image_id': 'fake_image',
    'is_default': True,
    'role': 'master',
    'max_node_count': 10,
    'min_node_count': 1
}


fake_responses = {
    '/v1/clusters/test/nodegroups/':
    {
        'GET': (
            {},
            {'nodegroups': [NODEGROUP1, NODEGROUP2]},
        ),
    },
    '/v1/clusters/test/nodegroups/%s' % NODEGROUP1['id']:
    {
        'GET': (
            {},
            NODEGROUP1
        ),
    },
    '/v1/clusters/test/nodegroups/%s' % NODEGROUP1['name']:
    {
        'GET': (
            {},
            NODEGROUP1
        ),
    },
    '/v1/clusters/test/nodegroups/?limit=2':
    {
        'GET': (
            {},
            {'nodegroups': [NODEGROUP1, NODEGROUP2]},
        ),
    },
    '/v1/clusters/test/nodegroups/?marker=%s' % NODEGROUP2['uuid']:
    {
        'GET': (
            {},
            {'nodegroups': [NODEGROUP1, NODEGROUP2]},
        ),
    },
    '/v1/clusters/test/nodegroups/?limit=2&marker=%s' % NODEGROUP2['uuid']:
    {
        'GET': (
            {},
            {'nodegroups': [NODEGROUP1, NODEGROUP2]},
        ),
    },
    '/v1/clusters/test/nodegroups/?sort_dir=asc':
    {
        'GET': (
            {},
            {'nodegroups': [NODEGROUP1, NODEGROUP2]},
        ),
    },
    '/v1/clusters/test/nodegroups/?sort_key=uuid':
    {
        'GET': (
            {},
            {'nodegroups': [NODEGROUP1, NODEGROUP2]},
        ),
    },
    '/v1/clusters/test/nodegroups/?sort_key=uuid&sort_dir=desc':
    {
        'GET': (
            {},
            {'nodegroups': [NODEGROUP2, NODEGROUP1]},
        ),
    },
}


class NodeGroupManagerTest(testtools.TestCase):

    def setUp(self):
        super(NodeGroupManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = nodegroups.NodeGroupManager(self.api)
        self.cluster_id = 'test'
        self.base_path = '/v1/clusters/test/nodegroups/'

    def test_nodegroup_list(self):
        clusters = self.mgr.list(self.cluster_id)
        expect = [
            ('GET', self.base_path, {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(clusters, matchers.HasLength(2))

    def _test_nodegroup_list_with_filters(self, cluster_id, limit=None,
                                          marker=None, sort_key=None,
                                          sort_dir=None, detail=False,
                                          expect=[]):
        nodegroup_filter = self.mgr.list(cluster_id,
                                         limit=limit,
                                         marker=marker,
                                         sort_key=sort_key,
                                         sort_dir=sort_dir,
                                         detail=detail)
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodegroup_filter, matchers.HasLength(2))

    def test_nodegroup_list_with_limit(self):
        expect = [
            ('GET', self.base_path + '?limit=2', {}, None),
        ]
        self._test_nodegroup_list_with_filters(
            self.cluster_id,
            limit=2,
            expect=expect)

    def test_nodegroup_list_with_marker(self):
        filter_ = '?marker=%s' % NODEGROUP2['uuid']
        expect = [
            ('GET', self.base_path + filter_, {}, None),
        ]
        self._test_nodegroup_list_with_filters(
            self.cluster_id,
            marker=NODEGROUP2['uuid'],
            expect=expect)

    def test_nodegroup_list_with_marker_limit(self):
        filter_ = '?limit=2&marker=%s' % NODEGROUP2['uuid']
        expect = [
            ('GET', self.base_path + filter_, {}, None),
        ]
        self._test_nodegroup_list_with_filters(
            self.cluster_id,
            limit=2, marker=NODEGROUP2['uuid'],
            expect=expect)

    def test_nodegroup_list_with_sort_dir(self):
        expect = [
            ('GET', '/v1/clusters/test/nodegroups/?sort_dir=asc', {}, None),
        ]
        self._test_nodegroup_list_with_filters(
            self.cluster_id,
            sort_dir='asc',
            expect=expect)

    def test_nodegroup_list_with_sort_key(self):
        expect = [
            ('GET', '/v1/clusters/test/nodegroups/?sort_key=uuid', {}, None),
        ]
        self._test_nodegroup_list_with_filters(
            self.cluster_id,
            sort_key='uuid',
            expect=expect)

    def test_nodegroup_list_with_sort_key_dir(self):
        expect = [
            ('GET', self.base_path + '?sort_key=uuid&sort_dir=desc', {}, None),
        ]
        self._test_nodegroup_list_with_filters(
            self.cluster_id,
            sort_key='uuid', sort_dir='desc',
            expect=expect)

    def test_nodegroup_show_by_name(self):
        nodegroup = self.mgr.get(self.cluster_id, NODEGROUP1['name'])
        expect = [
            ('GET', self.base_path + '%s' % NODEGROUP1['name'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NODEGROUP1['name'], nodegroup.name)

    def test_nodegroup_show_by_id(self):
        nodegroup = self.mgr.get(self.cluster_id, NODEGROUP1['id'])
        expect = [
            ('GET', self.base_path + '%s' % NODEGROUP1['id'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NODEGROUP1['name'], nodegroup.name)
