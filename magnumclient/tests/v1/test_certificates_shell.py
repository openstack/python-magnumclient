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

from magnumclient.common import cliutils as utils
from magnumclient.tests.v1 import shell_test_base
from magnumclient.v1 import certificates_shell


class ShellTest(shell_test_base.TestCommandLineArgument):

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.get')
    def test_ca_show_success(self, mock_cert_get, mock_bay_get):
        mockbay = mock.MagicMock()
        mockbay.status = "CREATE_COMPLETE"
        mockbay.uuid = "xxx"
        mock_bay_get.return_value = mockbay
        self._test_arg_success('ca-show '
                               '--bay xxx')
        expected_args = {}
        expected_args['cluster_uuid'] = mockbay.uuid
        mock_cert_get.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.get')
    def test_cluster_ca_show_success(self, mock_cert_get, mock_cluster_get):
        mockcluster = mock.MagicMock()
        mockcluster.status = "CREATE_COMPLETE"
        mockcluster.uuid = "xxx"
        mock_cluster_get.return_value = mockcluster
        self._test_arg_success('ca-show '
                               '--cluster xxx')
        expected_args = {}
        expected_args['cluster_uuid'] = mockcluster.uuid
        mock_cert_get.assert_called_once_with(**expected_args)

    @mock.patch('os.path.isfile')
    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.create')
    def test_ca_sign_success(
        self, mock_cert_create, mock_bay_get, mock_isfile):
        mock_isfile.return_value = True
        mockbay = mock.MagicMock()
        mockbay.status = "CREATE_COMPLETE"
        mockbay.uuid = "xxx"
        mock_bay_get.return_value = mockbay

        fake_csr = 'fake-csr'
        mock_file = mock.mock_open(read_data=fake_csr)
        with mock.patch.object(certificates_shell, 'open', mock_file):
            self._test_arg_success('ca-sign '
                                   '--csr path/csr.pem '
                                   '--bay xxx')
            expected_args = {}
            expected_args['cluster_uuid'] = mockbay.uuid
            expected_args['csr'] = fake_csr
            mock_cert_create.assert_called_once_with(**expected_args)

    @mock.patch('os.path.isfile')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.create')
    def test_cluster_ca_sign_success(
        self, mock_cert_create, mock_cluster_get, mock_isfile):
        mock_isfile.return_value = True
        mockcluster = mock.MagicMock()
        mockcluster.status = "CREATE_COMPLETE"
        mockcluster.uuid = "xxx"
        mock_cluster_get.return_value = mockcluster

        fake_csr = 'fake-csr'
        mock_file = mock.mock_open(read_data=fake_csr)
        with mock.patch.object(certificates_shell, 'open', mock_file):
            self._test_arg_success('ca-sign '
                                   '--csr path/csr.pem '
                                   '--cluster xxx')
            expected_args = {}
            expected_args['cluster_uuid'] = mockcluster.uuid
            expected_args['csr'] = fake_csr
            mock_cert_create.assert_called_once_with(**expected_args)

    @mock.patch('os.path.isfile')
    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.create')
    def test_ca_sign_with_not_csr(
        self, mock_cert_create, mock_bay_get, mock_isfile):
        mock_isfile.return_value = False
        mockbay = mock.MagicMock()
        mockbay.status = "CREATE_COMPLETE"
        mock_bay_get.return_value = mockbay

        fake_csr = 'fake-csr'
        mock_file = mock.mock_open(read_data=fake_csr)
        with mock.patch.object(certificates_shell, 'open', mock_file):
            self._test_arg_success('ca-sign '
                                   '--csr path/csr.pem '
                                   '--bay xxx')
            mock_isfile.assert_called_once_with('path/csr.pem')
            mock_file.assert_not_called()
            mock_cert_create.assert_not_called()

    @mock.patch('os.path.isfile')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.create')
    def test_cluster_ca_sign_with_not_csr(
        self, mock_cert_create, mock_cluster_get, mock_isfile):
        mock_isfile.return_value = False
        mockcluster = mock.MagicMock()
        mockcluster.status = "CREATE_COMPLETE"
        mock_cluster_get.return_value = mockcluster

        fake_csr = 'fake-csr'
        mock_file = mock.mock_open(read_data=fake_csr)
        with mock.patch.object(certificates_shell, 'open', mock_file):
            self._test_arg_success('ca-sign '
                                   '--csr path/csr.pem '
                                   '--cluster xxx')
            mock_isfile.assert_called_once_with('path/csr.pem')
            mock_file.assert_not_called()
            mock_cert_create.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.get')
    def test_ca_show_failure_with_invalid_field(self, mock_cert_get,
                                                mock_cluster_get):
        _error_msg = [".*?^--cluster or --bay"]
        self.assertRaises(utils.MissingArgs,
                          self._test_arg_failure,
                          'ca-show',
                          _error_msg)
        mock_cert_get.assert_not_called()
        mock_cluster_get.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.rotate_ca')
    def test_ca_rotate(self, mock_rotate_ca, mock_cluster_get):
        mockcluster = mock.MagicMock()
        mockcluster.status = "CREATE_COMPLETE"
        mockcluster.uuid = "xxx"
        mock_cluster_get.return_value = mockcluster
        mock_rotate_ca.return_value = None
        self._test_arg_success('ca-rotate '
                               '--cluster xxx')
        expected_args = {}
        expected_args['cluster_uuid'] = mockcluster.uuid
        mock_rotate_ca.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.rotate_ca')
    def test_ca_rotate_no_cluster_arg(self, mock_rotate_ca, mock_cluster_get):
        _error_msg = [
            (".*(error: argument --cluster is required|"  # py27 compatibility
             "error: the following arguments are required: --cluster).*"),
            ".*Try 'magnum help ca-rotate' for more information.*"
        ]
        self._test_arg_failure('ca-rotate', _error_msg)
        mock_rotate_ca.assert_not_called()
        mock_cluster_get.assert_not_called()
