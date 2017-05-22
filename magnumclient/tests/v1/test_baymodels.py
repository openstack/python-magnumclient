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
from magnumclient.v1 import baymodels

BAYMODEL1 = {'id': 123,
             'uuid': '66666666-7777-8888-9999-000000000001',
             'name': 'baymodel1',
             'image_id': 'baymodel1-image',
             'master_flavor_id': 'm1.tiny',
             'flavor_id': 'm1.small',
             'keypair_id': 'keypair1',
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
             'floating_ip_enabled': True,
             }

BAYMODEL2 = {'id': 124,
             'uuid': '66666666-7777-8888-9999-000000000002',
             'name': 'baymodel2',
             'image_id': 'baymodel2-image',
             'flavor_id': 'm2.small',
             'master_flavor_id': 'm2.tiny',
             'keypair_id': 'keypair2',
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

CREATE_BAYMODEL = copy.deepcopy(BAYMODEL1)
del CREATE_BAYMODEL['id']
del CREATE_BAYMODEL['uuid']

UPDATED_BAYMODEL = copy.deepcopy(BAYMODEL1)
NEW_NAME = 'newbay'
UPDATED_BAYMODEL['name'] = NEW_NAME

fake_responses = {
    '/v1/baymodels':
    {
        'GET': (
            {},
            {'baymodels': [BAYMODEL1, BAYMODEL2]},
        ),
        'POST': (
            {},
            CREATE_BAYMODEL,
        ),
    },
    '/v1/baymodels/%s' % BAYMODEL1['id']:
    {
        'GET': (
            {},
            BAYMODEL1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_BAYMODEL,
        ),
    },
    '/v1/baymodels/%s' % BAYMODEL1['name']:
    {
        'GET': (
            {},
            BAYMODEL1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_BAYMODEL,
        ),
    },
    '/v1/baymodels/detail':
    {
        'GET': (
            {},
            {'baymodels': [BAYMODEL1, BAYMODEL2]},
        ),
    },
    '/v1/baymodels/?limit=2':
    {
        'GET': (
            {},
            {'baymodels': [BAYMODEL1, BAYMODEL2]},
        ),
    },
    '/v1/baymodels/?marker=%s' % BAYMODEL2['uuid']:
    {
        'GET': (
            {},
            {'baymodels': [BAYMODEL1, BAYMODEL2]},
        ),
    },
    '/v1/baymodels/?limit=2&marker=%s' % BAYMODEL2['uuid']:
    {
        'GET': (
            {},
            {'baymodels': [BAYMODEL1, BAYMODEL2]},
        ),
    },
    '/v1/baymodels/?sort_dir=asc':
    {
        'GET': (
            {},
            {'baymodels': [BAYMODEL1, BAYMODEL2]},
        ),
    },
    '/v1/baymodels/?sort_key=uuid':
    {
        'GET': (
            {},
            {'baymodels': [BAYMODEL1, BAYMODEL2]},
        ),
    },
    '/v1/baymodels/?sort_key=uuid&sort_dir=desc':
    {
        'GET': (
            {},
            {'baymodels': [BAYMODEL2, BAYMODEL1]},
        ),
    },
}


class BayModelManagerTest(testtools.TestCase):

    def setUp(self):
        super(BayModelManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = baymodels.BayModelManager(self.api)

    def test_baymodel_list(self):
        baymodels = self.mgr.list()
        expect = [
            ('GET', '/v1/baymodels', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(baymodels, matchers.HasLength(2))

    def _test_baymodel_list_with_filters(
            self, limit=None, marker=None,
            sort_key=None, sort_dir=None,
            detail=False, expect=[]):
        baymodels_filter = self.mgr.list(limit=limit, marker=marker,
                                         sort_key=sort_key,
                                         sort_dir=sort_dir,
                                         detail=detail)
        self.assertEqual(expect, self.api.calls)
        self.assertThat(baymodels_filter, matchers.HasLength(2))

    def test_baymodel_list_with_detail(self):
        expect = [
            ('GET', '/v1/baymodels/detail', {}, None),
        ]
        self._test_baymodel_list_with_filters(
            detail=True,
            expect=expect)

    def test_baymodel_list_with_limit(self):
        expect = [
            ('GET', '/v1/baymodels/?limit=2', {}, None),
        ]
        self._test_baymodel_list_with_filters(
            limit=2,
            expect=expect)

    def test_baymodel_list_with_marker(self):
        expect = [
            ('GET', '/v1/baymodels/?marker=%s' % BAYMODEL2['uuid'], {}, None),
        ]
        self._test_baymodel_list_with_filters(
            marker=BAYMODEL2['uuid'],
            expect=expect)

    def test_baymodel_list_with_marker_limit(self):
        expect = [
            ('GET', '/v1/baymodels/?limit=2&marker=%s' % BAYMODEL2['uuid'],
             {}, None),
        ]
        self._test_baymodel_list_with_filters(
            limit=2, marker=BAYMODEL2['uuid'],
            expect=expect)

    def test_baymodel_list_with_sort_dir(self):
        expect = [
            ('GET', '/v1/baymodels/?sort_dir=asc', {}, None),
        ]
        self._test_baymodel_list_with_filters(
            sort_dir='asc',
            expect=expect)

    def test_baymodel_list_with_sort_key(self):
        expect = [
            ('GET', '/v1/baymodels/?sort_key=uuid', {}, None),
        ]
        self._test_baymodel_list_with_filters(
            sort_key='uuid',
            expect=expect)

    def test_baymodel_list_with_sort_key_dir(self):
        expect = [
            ('GET', '/v1/baymodels/?sort_key=uuid&sort_dir=desc', {}, None),
        ]
        self._test_baymodel_list_with_filters(
            sort_key='uuid', sort_dir='desc',
            expect=expect)

    def test_baymodel_show_by_id(self):
        baymodel = self.mgr.get(BAYMODEL1['id'])
        expect = [
            ('GET', '/v1/baymodels/%s' % BAYMODEL1['id'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(BAYMODEL1['name'], baymodel.name)
        self.assertEqual(BAYMODEL1['image_id'], baymodel.image_id)
        self.assertEqual(BAYMODEL1['docker_volume_size'],
                         baymodel.docker_volume_size)
        self.assertEqual(BAYMODEL1['docker_storage_driver'],
                         baymodel.docker_storage_driver)
        self.assertEqual(BAYMODEL1['fixed_network'], baymodel.fixed_network)
        self.assertEqual(BAYMODEL1['fixed_subnet'], baymodel.fixed_subnet)
        self.assertEqual(BAYMODEL1['coe'], baymodel.coe)
        self.assertEqual(BAYMODEL1['http_proxy'], baymodel.http_proxy)
        self.assertEqual(BAYMODEL1['https_proxy'], baymodel.https_proxy)
        self.assertEqual(BAYMODEL1['no_proxy'], baymodel.no_proxy)
        self.assertEqual(BAYMODEL1['network_driver'], baymodel.network_driver)
        self.assertEqual(BAYMODEL1['volume_driver'], baymodel.volume_driver)
        self.assertEqual(BAYMODEL1['labels'], baymodel.labels)
        self.assertEqual(BAYMODEL1['tls_disabled'], baymodel.tls_disabled)
        self.assertEqual(BAYMODEL1['public'], baymodel.public)
        self.assertEqual(BAYMODEL1['registry_enabled'],
                         baymodel.registry_enabled)
        self.assertEqual(BAYMODEL1['master_lb_enabled'],
                         baymodel.master_lb_enabled)
        self.assertEqual(BAYMODEL1['floating_ip_enabled'],
                         baymodel.floating_ip_enabled)

    def test_baymodel_show_by_name(self):
        baymodel = self.mgr.get(BAYMODEL1['name'])
        expect = [
            ('GET', '/v1/baymodels/%s' % BAYMODEL1['name'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(BAYMODEL1['name'], baymodel.name)
        self.assertEqual(BAYMODEL1['image_id'], baymodel.image_id)
        self.assertEqual(BAYMODEL1['docker_volume_size'],
                         baymodel.docker_volume_size)
        self.assertEqual(BAYMODEL1['docker_storage_driver'],
                         baymodel.docker_storage_driver)
        self.assertEqual(BAYMODEL1['fixed_network'], baymodel.fixed_network)
        self.assertEqual(BAYMODEL1['fixed_subnet'], baymodel.fixed_subnet)
        self.assertEqual(BAYMODEL1['coe'], baymodel.coe)
        self.assertEqual(BAYMODEL1['http_proxy'], baymodel.http_proxy)
        self.assertEqual(BAYMODEL1['https_proxy'], baymodel.https_proxy)
        self.assertEqual(BAYMODEL1['no_proxy'], baymodel.no_proxy)
        self.assertEqual(BAYMODEL1['network_driver'], baymodel.network_driver)
        self.assertEqual(BAYMODEL1['volume_driver'], baymodel.volume_driver)
        self.assertEqual(BAYMODEL1['labels'], baymodel.labels)
        self.assertEqual(BAYMODEL1['tls_disabled'], baymodel.tls_disabled)
        self.assertEqual(BAYMODEL1['public'], baymodel.public)
        self.assertEqual(BAYMODEL1['registry_enabled'],
                         baymodel.registry_enabled)
        self.assertEqual(BAYMODEL1['master_lb_enabled'],
                         baymodel.master_lb_enabled)
        self.assertEqual(BAYMODEL1['floating_ip_enabled'],
                         baymodel.floating_ip_enabled)

    def test_baymodel_create(self):
        baymodel = self.mgr.create(**CREATE_BAYMODEL)
        expect = [
            ('POST', '/v1/baymodels', {}, CREATE_BAYMODEL),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(baymodel)
        self.assertEqual(BAYMODEL1['docker_volume_size'],
                         baymodel.docker_volume_size)
        self.assertEqual(BAYMODEL1['docker_storage_driver'],
                         baymodel.docker_storage_driver)

    def test_baymodel_create_fail(self):
        CREATE_BAYMODEL_FAIL = copy.deepcopy(CREATE_BAYMODEL)
        CREATE_BAYMODEL_FAIL["wrong_key"] = "wrong"
        self.assertRaisesRegex(exceptions.InvalidAttribute,
                               ("Key must be in %s" %
                                ','.join(baymodels.CREATION_ATTRIBUTES)),
                               self.mgr.create, **CREATE_BAYMODEL_FAIL)
        self.assertEqual([], self.api.calls)

    def test_baymodel_delete_by_id(self):
        baymodel = self.mgr.delete(BAYMODEL1['id'])
        expect = [
            ('DELETE', '/v1/baymodels/%s' % BAYMODEL1['id'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(baymodel)

    def test_baymodel_delete_by_name(self):
        baymodel = self.mgr.delete(BAYMODEL1['name'])
        expect = [
            ('DELETE', '/v1/baymodels/%s' % BAYMODEL1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(baymodel)

    def test_baymodel_update(self):
        patch = {'op': 'replace',
                 'value': NEW_NAME,
                 'path': '/name'}
        baymodel = self.mgr.update(id=BAYMODEL1['id'], patch=patch)
        expect = [
            ('PATCH', '/v1/baymodels/%s' % BAYMODEL1['id'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_NAME, baymodel.name)
