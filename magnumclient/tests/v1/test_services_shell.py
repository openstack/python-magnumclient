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


class ShellTest(shell_test_base.TestCommandLineArgument):

    @mock.patch('magnumclient.v1.services.ServiceManager.list')
    def test_coe_service_list_success(self, mock_list):
        self._test_arg_success('coe-service-list --bay bay_ident')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.list')
    def test_coe_service_list_failure(self, mock_list):
        self._test_arg_failure('coe-service-list --bay bay_ident --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.services.ServiceManager.create')
    def test_coe_service_create_success(self, mock_create, mock_get):
        mockbay = mock.MagicMock()
        mockbay.status = "CREATE_COMPLETE"
        mock_get.return_value = mockbay
        self._test_arg_success('coe-service-create '
                               '--bay xxx '
                               '--manifest test '
                               '--manifest-url test_url')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.create')
    def test_coe_service_create_failure_few_arg(self, mock_create):
        self._test_arg_failure('coe-service-create '
                               '--manifest test '
                               '--manifest-url test_url',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.delete')
    def test_coe_service_delete_success(self, mock_delete):
        self._test_arg_success('coe-service-delete xxx --bay zzz')
        self.assertTrue(mock_delete.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.delete')
    def test_coe_service_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('coe-service-delete xxx',
                               self._mandatory_arg_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.get')
    def test_coe_service_show_success(self, mock_show):
        self._test_arg_success('coe-service-show xxx --bay zzz')
        self.assertTrue(mock_show.called)
        self.assertEqual(1, mock_show.call_count)

    @mock.patch('magnumclient.v1.services.ServiceManager.get')
    def test_coe_service_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('coe-service-show xxx',
                               self._mandatory_arg_error)
        self.assertFalse(mock_show.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.update')
    def test_coe_service_update_success(self, mock_update):
        self._test_arg_success('coe-service-update xxx --bay zzz'
                               ' replace xxx=xxx')
        self.assertTrue(mock_update.called)
        self.assertEqual(1, mock_update.call_count)

    @mock.patch('magnumclient.v1.services.ServiceManager.update')
    def test_coe_service_update_failure_no_arg(self, mock_update):
        self._test_arg_failure('coe-service-update xxx',
                               self._few_argument_error)
        self.assertFalse(mock_update.called)
