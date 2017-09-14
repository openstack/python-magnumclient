# Copyright 2015 NEC Corporation.  All rights reserved.
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

import mock

from magnumclient.osc.v1 import certificates as osc_certificates
from magnumclient.tests.osc.unit.v1 import fakes as magnum_fakes


class TestCertificate(magnum_fakes.TestMagnumClientOSCV1):

    def setUp(self):
        super(TestCertificate, self).setUp()

        self.clusters_mock = self.app.client_manager.container_infra.clusters


class TestRotateCa(TestCertificate):

    def setUp(self):
        super(TestRotateCa, self).setUp()

        attr = dict()
        attr['name'] = 'fake-cluster-1'
        self._cluster = magnum_fakes.FakeCluster.create_one_cluster(attr)

        self.clusters_mock.get = mock.Mock()
        self.clusters_mock.get.return_value = self._cluster

        self.cmd = osc_certificates.RotateCa(self.app, None)

    def test_rotate_ca(self):
        arglist = ['fake-cluster']
        verifylist = [
            ('cluster', 'fake-cluster')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.get.assert_called_once_with('fake-cluster')

    def test_rotate_ca_missing_args(self):
        arglist = []
        verifylist = []
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestShowCa(TestCertificate):

    def setUp(self):
        super(TestShowCa, self).setUp()

        attr = dict()
        attr['name'] = 'fake-cluster-1'
        self._cluster = magnum_fakes.FakeCluster.create_one_cluster(attr)

        self.clusters_mock.get = mock.Mock()
        self.clusters_mock.get.return_value = self._cluster

        self.cmd = osc_certificates.ShowCa(self.app, None)

    def test_show_ca(self):
        arglist = ['fake-cluster']
        verifylist = [
            ('cluster', 'fake-cluster')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.get.assert_called_once_with('fake-cluster')

    def test_show_ca_missing_args(self):
        arglist = []
        verifylist = []
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestSignCa(TestCertificate):

    test_csr_path = 'magnumclient/tests/test_csr/test.csr'

    def setUp(self):
        super(TestSignCa, self).setUp()

        attr = dict()
        attr['name'] = 'fake-cluster-1'
        self._cluster = magnum_fakes.FakeCluster.create_one_cluster(attr)

        self.clusters_mock.get = mock.Mock()
        self.clusters_mock.get.return_value = self._cluster

        self.cmd = osc_certificates.SignCa(self.app, None)

    def test_sign_ca(self):
        arglist = ['fake-cluster', self.test_csr_path]
        verifylist = [
            ('cluster', 'fake-cluster'),
            ('csr', self.test_csr_path)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.get.assert_called_once_with('fake-cluster')

    def test_sign_ca_without_csr(self):
        arglist = ['fake-cluster']
        verifylist = [
            ('cluster', 'fake-cluster')
        ]
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_sign_ca_without_cluster(self):
        arglist = [self.test_csr_path]
        verifylist = [
            ('csr', self.test_csr_path)
        ]
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_show_ca_missing_args(self):
        arglist = []
        verifylist = []
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)
