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

from magnumclient import exceptions
from magnumclient.tests.v1 import shell_test_base


class ShellTest(shell_test_base.TestCommandLineArgument):

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.pods.PodManager.list')
    def test_pod_list_success(self, mock_list, mock_get):
        mockbay = mock.MagicMock()
        mockbay.status = "CREATE_COMPLETE"
        mock_get.return_value = mockbay
        self._test_arg_success('pod-list --bay bay_ident')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.pods.PodManager.list')
    def test_pod_list_failure(self, mock_list):
        self._test_arg_failure('pod-list --bay bay_ident --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.pods.PodManager.list')
    def test_pod_list_failure_invalid_bay_status(self, mock_list, mock_get):
        mockbay = mock.MagicMock()
        mockbay.status = "CREATE_IN_PROGRESS"
        mock_get.return_value = mockbay
        self.assertRaises(exceptions.InvalidAttribute, self._test_arg_failure,
                          'pod-list --bay bay_ident', self._bay_status_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.pods.PodManager.create')
    def test_pod_create_success(self, mock_list, mock_get):
        mockbay = mock.MagicMock()
        mockbay.status = "CREATE_COMPLETE"
        mock_get.return_value = mockbay
        self._test_arg_success('pod-create '
                               '--bay xxx '
                               '--manifest test '
                               '--manifest-url test_url')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.pods.PodManager.create')
    def test_pod_create_failure_few_arg(self, mock_list, mock_get):
        self._test_arg_failure('pod-create '
                               '--manifest test '
                               '--manifest-url test_url',
                               self._mandatory_arg_error)
        self.assertFalse(mock_list.called)

        self._test_arg_failure('pod-create '
                               'bay xxx '
                               '--manifest-url test_url',
                               self._mandatory_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.pods.PodManager.create')
    def test_pod_create_failure_invalid_bay_status(self, mock_list, mock_get):
        mockbay = mock.MagicMock()
        mockbay.status = "CREATE_IN_PROGRESS"
        mock_get.return_value = mockbay
        self.assertRaises(exceptions.InvalidAttribute, self._test_arg_failure,
                          'pod-create --bay xxx '
                          '--manifest test '
                          '--manifest-url test_url',
                          self._bay_status_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.pods.PodManager.delete')
    def test_pod_delete_success(self, mock_delete):
        self._test_arg_success('pod-delete xxx --bay zzz')
        self.assertTrue(mock_delete.called)

    @mock.patch('magnumclient.v1.pods.PodManager.delete')
    def test_pod_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('pod-delete xxx', self._mandatory_arg_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.pods.PodManager.update')
    def test_pod_update_success(self, mock_update):
        self._test_arg_success('pod-update xxx --bay zzz replace xxx=xxx')
        self.assertTrue(mock_update.called)
        self.assertEqual(1, mock_update.call_count)

    @mock.patch('magnumclient.v1.pods.PodManager.update')
    def test_pod_update_failure_no_arg(self, mock_update):
        self._test_arg_failure('pod-update xxx', self._few_argument_error)
        self.assertFalse(mock_update.called)

    @mock.patch('magnumclient.v1.pods.PodManager.get')
    def test_pod_show_success(self, mock_show):
        self._test_arg_success('pod-show xxx --bay zzz')
        self.assertTrue(mock_show.called)

    @mock.patch('magnumclient.v1.pods.PodManager.get')
    def test_pod_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('pod-show', self._few_argument_error)
        self.assertFalse(mock_show.called)
