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

from magnumclient import exceptions
from magnumclient.tests import utils
from magnumclient.v1 import certificates


CERT1 = {
    'cluster_uuid': '5d12f6fd-a196-4bf0-ae4c-1f639a523a53',
    'pem': 'fake-pem'
}
CERT2 = {
    'cluster_uuid': '5d12f6fd-a196-4bf0-ae4c-1f639a523a53',
    'pem': 'fake-pem',
    'csr': 'fake-csr',
}

CREATE_CERT = {'cluster_uuid': '5d12f6fd-a196-4bf0-ae4c-1f639a523a53',
               'csr': 'fake-csr'}

CREATE_BACKWARDS_CERT = {
    'bay_uuid': '5d12f6fd-a196-4bf0-ae4c-1f639a523a53',
    'csr': 'fake-csr'
}

fake_responses = {
    '/v1/certificates':
    {
        'POST': (
            {},
            CERT2,
        )
    },
    '/v1/certificates/%s' % CERT1['cluster_uuid']:
    {
        'GET': (
            {},
            CERT1
        ),
        'PATCH': (
            {},
            None,
        )
    }
}


class CertificateManagerTest(testtools.TestCase):

    def setUp(self):
        super(CertificateManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = certificates.CertificateManager(self.api)

    def test_cert_show_by_id(self):
        cert = self.mgr.get(CERT1['cluster_uuid'])
        expect = [
            ('GET', '/v1/certificates/%s' % CERT1['cluster_uuid'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CERT1['cluster_uuid'], cert.cluster_uuid)
        self.assertEqual(CERT1['pem'], cert.pem)

    def test_cert_create(self):
        cert = self.mgr.create(**CREATE_CERT)
        expect = [
            ('POST', '/v1/certificates', {}, CREATE_CERT),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CERT2['cluster_uuid'], cert.cluster_uuid)
        self.assertEqual(CERT2['pem'], cert.pem)
        self.assertEqual(CERT2['csr'], cert.csr)

    def test_cert_create_backwards_compatibility(self):
        # Using a CREATION_ATTRIBUTE of bay_uuid and expecting a
        # cluster_uuid in return
        cert = self.mgr.create(**CREATE_BACKWARDS_CERT)
        expect = [
            ('POST', '/v1/certificates', {}, CREATE_CERT),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CERT2['cluster_uuid'], cert.cluster_uuid)
        self.assertEqual(CERT2['csr'], cert.csr)

    def test_create_fail(self):
        create_cert_fail = copy.deepcopy(CREATE_CERT)
        create_cert_fail["wrong_key"] = "wrong"
        self.assertRaisesRegex(exceptions.InvalidAttribute,
                               ("Key must be in %s" %
                                ','.join(certificates.CREATION_ATTRIBUTES)),
                               self.mgr.create, **create_cert_fail)
        self.assertEqual([], self.api.calls)

    def test_rotate_ca(self):
        self.mgr.rotate_ca(cluster_uuid=CERT1['cluster_uuid'])
        expect = [
            ('PATCH', '/v1/certificates/%s' % CERT1['cluster_uuid'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
