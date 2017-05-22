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
from magnumclient.v1 import cluster_templates


CLUSTERTEMPLATE1 = {
    'id': 123,
    'uuid': '66666666-7777-8888-9999-000000000001',
    'name': 'clustertemplate1',
    'image_id': 'clustertemplate1-image',
    'master_flavor_id': 'm1.tiny',
    'flavor_id': 'm1.small',
    'external_network_id': 'd1f02cfb-d27f-4068-9332-84d907cb0e21',
    'fixed_network': 'private',
    'fixed_subnet': 'private-subnet',
    'network_driver': 'libnetwork',
    'volume_driver': 'rexray',
    'dns_nameserver': '8.8.1.1',
    'docker_volume_size': '71',
    'docker_storage_driver': 'devicemapper',
    'coe': 'swarm',
    'http_proxy': 'http_proxy',
    'https_proxy': 'https_proxy',
    'no_proxy': 'no_proxy',
    'labels': 'key1=val1,key11=val11',
    'tls_disabled': False,
    'public': False,
    'registry_enabled': False,
    'master_lb_enabled': True,
    'floating_ip_enabled': True
    }

CLUSTERTEMPLATE2 = {
    'id': 124,
    'uuid': '66666666-7777-8888-9999-000000000002',
    'name': 'clustertemplate2',
    'image_id': 'clustertemplate2-image',
    'flavor_id': 'm2.small',
    'master_flavor_id': 'm2.tiny',
    'external_network_id': 'd1f02cfb-d27f-4068-9332-84d907cb0e22',
    'fixed_network': 'private2',
    'network_driver': 'flannel',
    'volume_driver': 'cinder',
    'dns_nameserver': '8.8.1.2',
    'docker_volume_size': '50',
    'docker_storage_driver': 'overlay',
    'coe': 'kubernetes',
    'labels': 'key2=val2,key22=val22',
    'tls_disabled': True,
    'public': True,
    'registry_enabled': True}

CREATE_CLUSTERTEMPLATE = copy.deepcopy(CLUSTERTEMPLATE1)
del CREATE_CLUSTERTEMPLATE['id']
del CREATE_CLUSTERTEMPLATE['uuid']

UPDATED_CLUSTERTEMPLATE = copy.deepcopy(CLUSTERTEMPLATE1)
NEW_NAME = 'newcluster'
UPDATED_CLUSTERTEMPLATE['name'] = NEW_NAME

fake_responses = {
    '/v1/clustertemplates':
    {
        'GET': (
            {},
            {'clustertemplates': [CLUSTERTEMPLATE1, CLUSTERTEMPLATE2]},
        ),
        'POST': (
            {},
            CREATE_CLUSTERTEMPLATE,
        ),
    },
    '/v1/clustertemplates/%s' % CLUSTERTEMPLATE1['id']:
    {
        'GET': (
            {},
            CLUSTERTEMPLATE1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_CLUSTERTEMPLATE,
        ),
    },
    '/v1/clustertemplates/%s' % CLUSTERTEMPLATE1['name']:
    {
        'GET': (
            {},
            CLUSTERTEMPLATE1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_CLUSTERTEMPLATE,
        ),
    },
    '/v1/clustertemplates/detail':
    {
        'GET': (
            {},
            {'clustertemplates': [CLUSTERTEMPLATE1, CLUSTERTEMPLATE2]},
        ),
    },
    '/v1/clustertemplates/?limit=2':
    {
        'GET': (
            {},
            {'clustertemplates': [CLUSTERTEMPLATE1, CLUSTERTEMPLATE2]},
        ),
    },
    '/v1/clustertemplates/?marker=%s' % CLUSTERTEMPLATE2['uuid']:
    {
        'GET': (
            {},
            {'clustertemplates': [CLUSTERTEMPLATE1, CLUSTERTEMPLATE2]},
        ),
    },
    '/v1/clustertemplates/?limit=2&marker=%s' % CLUSTERTEMPLATE2['uuid']:
    {
        'GET': (
            {},
            {'clustertemplates': [CLUSTERTEMPLATE1, CLUSTERTEMPLATE2]},
        ),
    },
    '/v1/clustertemplates/?sort_dir=asc':
    {
        'GET': (
            {},
            {'clustertemplates': [CLUSTERTEMPLATE1, CLUSTERTEMPLATE2]},
        ),
    },
    '/v1/clustertemplates/?sort_key=uuid':
    {
        'GET': (
            {},
            {'clustertemplates': [CLUSTERTEMPLATE1, CLUSTERTEMPLATE2]},
        ),
    },
    '/v1/clustertemplates/?sort_key=uuid&sort_dir=desc':
    {
        'GET': (
            {},
            {'clustertemplates': [CLUSTERTEMPLATE2, CLUSTERTEMPLATE1]},
        ),
    },
}


class ClusterTemplateManagerTest(testtools.TestCase):

    def setUp(self):
        super(ClusterTemplateManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = cluster_templates.ClusterTemplateManager(self.api)

    def test_clustertemplate_list(self):
        clustertemplates = self.mgr.list()
        expect = [
            ('GET', '/v1/clustertemplates', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(clustertemplates, matchers.HasLength(2))

    def _test_clustertemplate_list_with_filters(
            self, limit=None, marker=None,
            sort_key=None, sort_dir=None,
            detail=False, expect=[]):
        clustertemplates_filter = self.mgr.list(limit=limit,
                                                marker=marker,
                                                sort_key=sort_key,
                                                sort_dir=sort_dir,
                                                detail=detail)
        self.assertEqual(expect, self.api.calls)
        self.assertThat(clustertemplates_filter, matchers.HasLength(2))

    def test_clustertemplate_list_with_detail(self):
        expect = [
            ('GET', '/v1/clustertemplates/detail', {}, None),
        ]
        self._test_clustertemplate_list_with_filters(
            detail=True,
            expect=expect)

    def test_clustertemplate_list_with_limit(self):
        expect = [
            ('GET', '/v1/clustertemplates/?limit=2', {}, None),
        ]
        self._test_clustertemplate_list_with_filters(
            limit=2,
            expect=expect)

    def test_clustertemplate_list_with_marker(self):
        expect = [
            ('GET',
             '/v1/clustertemplates/?marker=%s' % CLUSTERTEMPLATE2['uuid'],
             {},
             None),
        ]
        self._test_clustertemplate_list_with_filters(
            marker=CLUSTERTEMPLATE2['uuid'],
            expect=expect)

    def test_clustertemplate_list_with_marker_limit(self):
        expect = [
            ('GET',
             '/v1/clustertemplates/?limit=2&marker=%s' %
             CLUSTERTEMPLATE2['uuid'],
             {},
             None),
        ]
        self._test_clustertemplate_list_with_filters(
            limit=2, marker=CLUSTERTEMPLATE2['uuid'],
            expect=expect)

    def test_clustertemplate_list_with_sort_dir(self):
        expect = [
            ('GET', '/v1/clustertemplates/?sort_dir=asc', {}, None),
        ]
        self._test_clustertemplate_list_with_filters(
            sort_dir='asc',
            expect=expect)

    def test_clustertemplate_list_with_sort_key(self):
        expect = [
            ('GET', '/v1/clustertemplates/?sort_key=uuid', {}, None),
        ]
        self._test_clustertemplate_list_with_filters(
            sort_key='uuid',
            expect=expect)

    def test_clustertemplate_list_with_sort_key_dir(self):
        expect = [
            ('GET',
             '/v1/clustertemplates/?sort_key=uuid&sort_dir=desc',
             {},
             None),
        ]
        self._test_clustertemplate_list_with_filters(
            sort_key='uuid', sort_dir='desc',
            expect=expect)

    def test_clustertemplate_show_by_id(self):
        cluster_template = self.mgr.get(CLUSTERTEMPLATE1['id'])
        expect = [
            ('GET',
             '/v1/clustertemplates/%s' % CLUSTERTEMPLATE1['id'],
             {},
             None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CLUSTERTEMPLATE1['name'],
                         cluster_template.name)
        self.assertEqual(CLUSTERTEMPLATE1['image_id'],
                         cluster_template.image_id)
        self.assertEqual(CLUSTERTEMPLATE1['docker_volume_size'],
                         cluster_template.docker_volume_size)
        self.assertEqual(CLUSTERTEMPLATE1['docker_storage_driver'],
                         cluster_template.docker_storage_driver)
        self.assertEqual(CLUSTERTEMPLATE1['fixed_network'],
                         cluster_template.fixed_network)
        self.assertEqual(CLUSTERTEMPLATE1['fixed_subnet'],
                         cluster_template.fixed_subnet)
        self.assertEqual(CLUSTERTEMPLATE1['coe'],
                         cluster_template.coe)
        self.assertEqual(CLUSTERTEMPLATE1['http_proxy'],
                         cluster_template.http_proxy)
        self.assertEqual(CLUSTERTEMPLATE1['https_proxy'],
                         cluster_template.https_proxy)
        self.assertEqual(CLUSTERTEMPLATE1['no_proxy'],
                         cluster_template.no_proxy)
        self.assertEqual(CLUSTERTEMPLATE1['network_driver'],
                         cluster_template.network_driver)
        self.assertEqual(CLUSTERTEMPLATE1['volume_driver'],
                         cluster_template.volume_driver)
        self.assertEqual(CLUSTERTEMPLATE1['labels'],
                         cluster_template.labels)
        self.assertEqual(CLUSTERTEMPLATE1['tls_disabled'],
                         cluster_template.tls_disabled)
        self.assertEqual(CLUSTERTEMPLATE1['public'],
                         cluster_template.public)
        self.assertEqual(CLUSTERTEMPLATE1['registry_enabled'],
                         cluster_template.registry_enabled)
        self.assertEqual(CLUSTERTEMPLATE1['master_lb_enabled'],
                         cluster_template.master_lb_enabled)
        self.assertEqual(CLUSTERTEMPLATE1['floating_ip_enabled'],
                         cluster_template.floating_ip_enabled)

    def test_clustertemplate_show_by_name(self):
        cluster_template = self.mgr.get(CLUSTERTEMPLATE1['name'])
        expect = [
            ('GET',
             '/v1/clustertemplates/%s' % CLUSTERTEMPLATE1['name'],
             {},
             None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CLUSTERTEMPLATE1['name'],
                         cluster_template.name)
        self.assertEqual(CLUSTERTEMPLATE1['image_id'],
                         cluster_template.image_id)
        self.assertEqual(CLUSTERTEMPLATE1['docker_volume_size'],
                         cluster_template.docker_volume_size)
        self.assertEqual(CLUSTERTEMPLATE1['docker_storage_driver'],
                         cluster_template.docker_storage_driver)
        self.assertEqual(CLUSTERTEMPLATE1['fixed_network'],
                         cluster_template.fixed_network)
        self.assertEqual(CLUSTERTEMPLATE1['fixed_subnet'],
                         cluster_template.fixed_subnet)
        self.assertEqual(CLUSTERTEMPLATE1['coe'],
                         cluster_template.coe)
        self.assertEqual(CLUSTERTEMPLATE1['http_proxy'],
                         cluster_template.http_proxy)
        self.assertEqual(CLUSTERTEMPLATE1['https_proxy'],
                         cluster_template.https_proxy)
        self.assertEqual(CLUSTERTEMPLATE1['no_proxy'],
                         cluster_template.no_proxy)
        self.assertEqual(CLUSTERTEMPLATE1['network_driver'],
                         cluster_template.network_driver)
        self.assertEqual(CLUSTERTEMPLATE1['volume_driver'],
                         cluster_template.volume_driver)
        self.assertEqual(CLUSTERTEMPLATE1['labels'],
                         cluster_template.labels)
        self.assertEqual(CLUSTERTEMPLATE1['tls_disabled'],
                         cluster_template.tls_disabled)
        self.assertEqual(CLUSTERTEMPLATE1['public'],
                         cluster_template.public)
        self.assertEqual(CLUSTERTEMPLATE1['registry_enabled'],
                         cluster_template.registry_enabled)
        self.assertEqual(CLUSTERTEMPLATE1['master_lb_enabled'],
                         cluster_template.master_lb_enabled)
        self.assertEqual(CLUSTERTEMPLATE1['floating_ip_enabled'],
                         cluster_template.floating_ip_enabled)

    def test_clustertemplate_create(self):
        cluster_template = self.mgr.create(**CREATE_CLUSTERTEMPLATE)
        expect = [
            ('POST', '/v1/clustertemplates', {}, CREATE_CLUSTERTEMPLATE),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(cluster_template)
        self.assertEqual(CLUSTERTEMPLATE1['docker_volume_size'],
                         cluster_template.docker_volume_size)
        self.assertEqual(CLUSTERTEMPLATE1['docker_storage_driver'],
                         cluster_template.docker_storage_driver)

    def test_clustertemplate_create_with_keypair(self):
        cluster_template_with_keypair = dict()
        cluster_template_with_keypair.update(CREATE_CLUSTERTEMPLATE)
        cluster_template_with_keypair['keypair_id'] = 'test_key'

        cluster_template = self.mgr.create(**cluster_template_with_keypair)
        expect = [
            ('POST', '/v1/clustertemplates', {},
             cluster_template_with_keypair),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(cluster_template)
        self.assertEqual(CLUSTERTEMPLATE1['docker_volume_size'],
                         cluster_template.docker_volume_size)
        self.assertEqual(CLUSTERTEMPLATE1['docker_storage_driver'],
                         cluster_template.docker_storage_driver)

    def test_clustertemplate_create_fail(self):
        CREATE_CLUSTERTEMPLATE_FAIL = copy.deepcopy(CREATE_CLUSTERTEMPLATE)
        CREATE_CLUSTERTEMPLATE_FAIL["wrong_key"] = "wrong"
        self.assertRaisesRegex(
            exceptions.InvalidAttribute,
            ("Key must be in %s" %
             ','.join(cluster_templates.CREATION_ATTRIBUTES)),
            self.mgr.create, **CREATE_CLUSTERTEMPLATE_FAIL)
        self.assertEqual([], self.api.calls)

    def test_clustertemplate_delete_by_id(self):
        cluster_template = self.mgr.delete(CLUSTERTEMPLATE1['id'])
        expect = [
            ('DELETE',
             '/v1/clustertemplates/%s' % CLUSTERTEMPLATE1['id'],
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(cluster_template)

    def test_clustertemplate_delete_by_name(self):
        cluster_template = self.mgr.delete(CLUSTERTEMPLATE1['name'])
        expect = [
            ('DELETE',
             '/v1/clustertemplates/%s' % CLUSTERTEMPLATE1['name'],
             {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(cluster_template)

    def test_clustertemplate_update(self):
        patch = {'op': 'replace',
                 'value': NEW_NAME,
                 'path': '/name'}
        cluster_template = self.mgr.update(id=CLUSTERTEMPLATE1['id'],
                                           patch=patch)
        expect = [
            ('PATCH',
             '/v1/clustertemplates/%s' % CLUSTERTEMPLATE1['id'],
             {},
             patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_NAME, cluster_template.name)
