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
             'network_driver': 'libnetwork',
             'dns_nameserver': '8.8.1.1',
             'docker_volume_size': '71',
             'ssh_authorized_key': 'ssh-rsa AAAAB3NaC1yc2EAAAADAABAAABAQC'
                                   '0XRqg3tm+jlsOKGO81lPDH+KaSJs8qegZHtQw'
                                   '3Q7wvmjUqszP/H6NC/m+qiGp/sTitomSofMam'
                                   'YucqbeuM7nmJi+8Hb55y1xWoOZItvKJ+n4VKc'
                                   'Ma71G5/4EOQxuQ/sgW965OOO2Hq027yHOwzcR'
                                   '8vjlQUnTK0HijrbSTLxp/9kazWWraBS0AyXe6'
                                   'v0Zio4VeFrfpytB8RtAAA test1234@magnum',
             'coe': 'swarm',
             'http_proxy': 'http_proxy',
             'https_proxy': 'https_proxy',
             'no_proxy': 'no_proxy',
             'labels': 'key1=val1,key11=val11',
             'insecure': False,
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
             'dns_nameserver': '8.8.1.2',
             'docker_volume_size': '50',
             'ssh_authorized_key': 'ssh-rsa AAAAB3NzaC1ycEAAAADAQABAAABAQC'
                                   'v0XRqg3tm+jlsOKGO81lPDH+KaSJs8qegZHtQw'
                                   'n3Q7wvmjUqszP/H6NC/m+qiGp/sTitomSofMam'
                                   'DYucqbeuM7nmJi+8Hb55y1xWoOZItvKJ+n4VKc'
                                   'KMa71G5/4EOQxuQ/sgW965OOO2Hq027yHOwzcR'
                                   'X8vjlQUnTK0HijrbSTLxp/9kazWWraBS0AyXe6'
                                   'Jv0Zio4VeFrfpytB8RtAAA test1234@magnum',
             'coe': 'kubernetes',
             'labels': 'key2=val2,key22=val22',
             'insecure': True,
             }

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
        self.assertEqual(BAYMODEL1['fixed_network'], baymodel.fixed_network)
        self.assertEqual(BAYMODEL1['ssh_authorized_key'],
                         baymodel.ssh_authorized_key)
        self.assertEqual(BAYMODEL1['coe'], baymodel.coe)
        self.assertEqual(BAYMODEL1['http_proxy'], baymodel.http_proxy)
        self.assertEqual(BAYMODEL1['https_proxy'], baymodel.https_proxy)
        self.assertEqual(BAYMODEL1['no_proxy'], baymodel.no_proxy)
        self.assertEqual(BAYMODEL1['network_driver'], baymodel.network_driver)
        self.assertEqual(BAYMODEL1['labels'], baymodel.labels)
        self.assertEqual(BAYMODEL1['insecure'], baymodel.insecure)

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
        self.assertEqual(BAYMODEL1['fixed_network'], baymodel.fixed_network)
        self.assertEqual(BAYMODEL1['ssh_authorized_key'],
                         baymodel.ssh_authorized_key)
        self.assertEqual(BAYMODEL1['coe'], baymodel.coe)
        self.assertEqual(BAYMODEL1['http_proxy'], baymodel.http_proxy)
        self.assertEqual(BAYMODEL1['https_proxy'], baymodel.https_proxy)
        self.assertEqual(BAYMODEL1['no_proxy'], baymodel.no_proxy)
        self.assertEqual(BAYMODEL1['network_driver'], baymodel.network_driver)
        self.assertEqual(BAYMODEL1['labels'], baymodel.labels)
        self.assertEqual(BAYMODEL1['insecure'], baymodel.insecure)

    def test_baymodel_create(self):
        baymodel = self.mgr.create(**CREATE_BAYMODEL)
        expect = [
            ('POST', '/v1/baymodels', {}, CREATE_BAYMODEL),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(baymodel)
        self.assertEqual(BAYMODEL1['docker_volume_size'],
                         baymodel.docker_volume_size)

    def test_baymodel_create_fail(self):
        CREATE_BAYMODEL_FAIL = copy.deepcopy(CREATE_BAYMODEL)
        CREATE_BAYMODEL_FAIL["wrong_key"] = "wrong"
        self.assertRaisesRegexp(exceptions.InvalidAttribute,
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
