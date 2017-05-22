# Copyright 2015 IBM Corp
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
from magnumclient.v1 import clusters


CLUSTER1 = {'id': 123,
            'uuid': '66666666-7777-8888-9999-000000000001',
            'name': 'cluster1',
            'cluster_template_id': 'e74c40e0-d825-11e2-a28f-0800200c9a61',
            'stack_id': '5d12f6fd-a196-4bf0-ae4c-1f639a523a51',
            'api_address': '172.17.2.1',
            'node_addresses': ['172.17.2.3'],
            'node_count': 2,
            'master_count': 1,
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
            }

CREATE_CLUSTER = copy.deepcopy(CLUSTER1)
del CREATE_CLUSTER['id']
del CREATE_CLUSTER['uuid']
del CREATE_CLUSTER['stack_id']
del CREATE_CLUSTER['api_address']
del CREATE_CLUSTER['node_addresses']

UPDATED_CLUSTER = copy.deepcopy(CLUSTER1)
NEW_NAME = 'newcluster'
UPDATED_CLUSTER['name'] = NEW_NAME

fake_responses = {
    '/v1/clusters':
    {
        'GET': (
            {},
            {'clusters': [CLUSTER1, CLUSTER2]},
        ),
        'POST': (
            {},
            CREATE_CLUSTER,
        ),
    },
    '/v1/clusters/%s' % CLUSTER1['id']:
    {
        'GET': (
            {},
            CLUSTER1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_CLUSTER,
        ),
    },
    '/v1/clusters/%s/?rollback=True' % CLUSTER1['id']:
        {
            'PATCH': (
                {},
                UPDATED_CLUSTER,
            ),
        },
    '/v1/clusters/%s' % CLUSTER1['name']:
    {
        'GET': (
            {},
            CLUSTER1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_CLUSTER,
        ),
    },
    '/v1/clusters/?limit=2':
    {
        'GET': (
            {},
            {'clusters': [CLUSTER1, CLUSTER2]},
        ),
    },
    '/v1/clusters/?marker=%s' % CLUSTER2['uuid']:
    {
        'GET': (
            {},
            {'clusters': [CLUSTER1, CLUSTER2]},
        ),
    },
    '/v1/clusters/?limit=2&marker=%s' % CLUSTER2['uuid']:
    {
        'GET': (
            {},
            {'clusters': [CLUSTER1, CLUSTER2]},
        ),
    },
    '/v1/clusters/?sort_dir=asc':
    {
        'GET': (
            {},
            {'clusters': [CLUSTER1, CLUSTER2]},
        ),
    },
    '/v1/clusters/?sort_key=uuid':
    {
        'GET': (
            {},
            {'clusters': [CLUSTER1, CLUSTER2]},
        ),
    },
    '/v1/clusters/?sort_key=uuid&sort_dir=desc':
    {
        'GET': (
            {},
            {'clusters': [CLUSTER2, CLUSTER1]},
        ),
    },
}


class ClusterManagerTest(testtools.TestCase):

    def setUp(self):
        super(ClusterManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = clusters.ClusterManager(self.api)

    def test_cluster_list(self):
        clusters = self.mgr.list()
        expect = [
            ('GET', '/v1/clusters', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(clusters, matchers.HasLength(2))

    def _test_cluster_list_with_filters(self, limit=None, marker=None,
                                        sort_key=None, sort_dir=None,
                                        detail=False, expect=[]):
        clusters_filter = self.mgr.list(limit=limit,
                                        marker=marker,
                                        sort_key=sort_key,
                                        sort_dir=sort_dir,
                                        detail=detail)
        self.assertEqual(expect, self.api.calls)
        self.assertThat(clusters_filter, matchers.HasLength(2))

    def test_cluster_list_with_limit(self):
        expect = [
            ('GET', '/v1/clusters/?limit=2', {}, None),
        ]
        self._test_cluster_list_with_filters(
            limit=2,
            expect=expect)

    def test_cluster_list_with_marker(self):
        expect = [
            ('GET', '/v1/clusters/?marker=%s' % CLUSTER2['uuid'], {}, None),
        ]
        self._test_cluster_list_with_filters(
            marker=CLUSTER2['uuid'],
            expect=expect)

    def test_cluster_list_with_marker_limit(self):
        expect = [
            ('GET', '/v1/clusters/?limit=2&marker=%s' % CLUSTER2['uuid'],
             {},
             None),
        ]
        self._test_cluster_list_with_filters(
            limit=2, marker=CLUSTER2['uuid'],
            expect=expect)

    def test_cluster_list_with_sort_dir(self):
        expect = [
            ('GET', '/v1/clusters/?sort_dir=asc', {}, None),
        ]
        self._test_cluster_list_with_filters(
            sort_dir='asc',
            expect=expect)

    def test_cluster_list_with_sort_key(self):
        expect = [
            ('GET', '/v1/clusters/?sort_key=uuid', {}, None),
        ]
        self._test_cluster_list_with_filters(
            sort_key='uuid',
            expect=expect)

    def test_cluster_list_with_sort_key_dir(self):
        expect = [
            ('GET', '/v1/clusters/?sort_key=uuid&sort_dir=desc', {}, None),
        ]
        self._test_cluster_list_with_filters(
            sort_key='uuid', sort_dir='desc',
            expect=expect)

    def test_cluster_show_by_id(self):
        cluster = self.mgr.get(CLUSTER1['id'])
        expect = [
            ('GET', '/v1/clusters/%s' % CLUSTER1['id'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CLUSTER1['name'], cluster.name)
        self.assertEqual(CLUSTER1['cluster_template_id'],
                         cluster.cluster_template_id)

    def test_cluster_show_by_name(self):
        cluster = self.mgr.get(CLUSTER1['name'])
        expect = [
            ('GET', '/v1/clusters/%s' % CLUSTER1['name'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CLUSTER1['name'], cluster.name)
        self.assertEqual(CLUSTER1['cluster_template_id'],
                         cluster.cluster_template_id)

    def test_cluster_create(self):
        cluster = self.mgr.create(**CREATE_CLUSTER)
        expect = [
            ('POST', '/v1/clusters', {}, CREATE_CLUSTER),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(cluster)

    def test_cluster_create_with_keypair(self):
        cluster_with_keypair = dict()
        cluster_with_keypair.update(CREATE_CLUSTER)
        cluster_with_keypair['keypair'] = 'test_key'
        cluster = self.mgr.create(**cluster_with_keypair)
        expect = [
            ('POST', '/v1/clusters', {}, cluster_with_keypair),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(cluster)

    def test_cluster_create_with_discovery_url(self):
        cluster_with_discovery = dict()
        cluster_with_discovery.update(CREATE_CLUSTER)
        cluster_with_discovery['discovery_url'] = 'discovery_url'
        cluster = self.mgr.create(**cluster_with_discovery)
        expect = [
            ('POST', '/v1/clusters', {}, cluster_with_discovery),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(cluster)

    def test_cluster_create_with_cluster_create_timeout(self):
        cluster_with_timeout = dict()
        cluster_with_timeout.update(CREATE_CLUSTER)
        cluster_with_timeout['create_timeout'] = '15'
        cluster = self.mgr.create(**cluster_with_timeout)
        expect = [
            ('POST', '/v1/clusters', {}, cluster_with_timeout),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(cluster)

    def test_cluster_create_fail(self):
        CREATE_CLUSTER_FAIL = copy.deepcopy(CREATE_CLUSTER)
        CREATE_CLUSTER_FAIL["wrong_key"] = "wrong"
        self.assertRaisesRegex(exceptions.InvalidAttribute,
                               ("Key must be in %s" %
                                ','.join(clusters.CREATION_ATTRIBUTES)),
                               self.mgr.create, **CREATE_CLUSTER_FAIL)
        self.assertEqual([], self.api.calls)

    def test_cluster_delete_by_id(self):
        cluster = self.mgr.delete(CLUSTER1['id'])
        expect = [
            ('DELETE', '/v1/clusters/%s' % CLUSTER1['id'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(cluster)

    def test_cluster_delete_by_name(self):
        cluster = self.mgr.delete(CLUSTER1['name'])
        expect = [
            ('DELETE', '/v1/clusters/%s' % CLUSTER1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(cluster)

    def test_cluster_update(self):
        patch = {'op': 'replace',
                 'value': NEW_NAME,
                 'path': '/name'}
        cluster = self.mgr.update(id=CLUSTER1['id'], patch=patch)
        expect = [
            ('PATCH', '/v1/clusters/%s' % CLUSTER1['id'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_NAME, cluster.name)

    def test_cluster_update_with_rollback(self):
        patch = {'op': 'replace',
                 'value': NEW_NAME,
                 'path': '/name'}
        cluster = self.mgr.update(id=CLUSTER1['id'], patch=patch,
                                  rollback=True)
        expect = [
            ('PATCH', '/v1/clusters/%s/?rollback=True' % CLUSTER1['id'],
             {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_NAME, cluster.name)
