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

from magnumclient.tests.v1 import shell_test_base
from magnumclient.v1 import certificates_shell


class ShellTest(shell_test_base.TestCommandLineArgument):

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.get')
    def test_ca_show_success(self, mock_cert_get, mock_bay_get):
        mockbay = mock.MagicMock()
        mockbay.status = "CREATE_COMPLETE"
        mock_bay_get.return_value = mockbay
        self._test_arg_success('ca-show '
                               '--bay xxx')
        self.assertTrue(mock_cert_get.called)

    @mock.patch('os.path.isfile')
    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.create')
    def test_ca_sign_success(
        self, mock_cert_create, mock_bay_get, mock_isfile):
        mock_isfile.return_value = True
        mockbay = mock.MagicMock()
        mockbay.status = "CREATE_COMPLETE"
        mock_bay_get.return_value = mockbay

        fake_csr = 'fake-csr'
        file_mock = mock.mock_open(read_data=fake_csr)
        with mock.patch.object(certificates_shell, 'open', file_mock):
            self._test_arg_success('ca-sign '
                                   '--csr path/csr.pem '
                                   '--bay xxx')
            self.assertTrue(mock_cert_create.called)

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
        file_mock = mock.mock_open(read_data=fake_csr)
        with mock.patch.object(certificates_shell, 'open', file_mock):
            self._test_arg_success('ca-sign '
                                   '--csr path/csr.pem '
                                   '--bay xxx')
            mock_isfile.assert_called_once_with('path/csr.pem')
            self.assertFalse(file_mock.called)
            self.assertFalse(mock_cert_create.called)
