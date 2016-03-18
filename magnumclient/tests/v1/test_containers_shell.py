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

    @mock.patch('magnumclient.v1.containers.ContainerManager.list')
    def test_container_list_success(self, mock_list):
        self._test_arg_success('container-list')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.list')
    def test_container_list_success_with_arg(self, mock_list):
        self._test_arg_success('container-list '
                               '--marker some_uuid '
                               '--limit 1 '
                               '--sort-dir asc '
                               '--sort-key uuid')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.list')
    def test_container_list_failure_invalid_arg(self, mock_list):
        _error_msg = [
            '.*?^usage: magnum container-list ',
            '.*?^error: argument --sort-dir: invalid choice: ',
            ".*?^Try 'magnum help container-list' for more information."
            ]
        self._test_arg_failure('container-list --sort-dir aaa', _error_msg)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.list')
    def test_container_list_success_with_bay(self, mock_list):
        self._test_arg_success('container-list --bay bay_uuid')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.list')
    def test_container_list_failure(self, mock_list):
        self._test_arg_failure('container-list --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.containers.ContainerManager.create')
    def test_container_create_success(self, mock_create, mock_bay_get):
        mock_bay = mock.MagicMock()
        mock_bay.status = "CREATE_COMPLETE"
        mock_bay_get.return_value = mock_bay
        self._test_arg_success('container-create '
                               '--image test-image '
                               '--bay test-bay')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.containers.ContainerManager.create')
    def test_container_create_failure_without_image(self, mock_create,
                                                    mock_bay_get):
        mock_bay = mock.MagicMock()
        mock_bay.status = "CREATE_COMPLETE"
        mock_bay_get.return_value = mock_bay
        self._test_arg_failure('container-create '
                               '--bay test-bay',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.containers.ContainerManager.create')
    def test_container_create_failure_invalid_bay_status(self, mock_create,
                                                         mock_bay_get):
        mock_bay = mock.MagicMock()
        mock_bay.status = "CREATE_IN_PROGRESS"
        mock_bay_get.return_value = mock_bay
        self.assertRaises(exceptions.InvalidAttribute, self._test_arg_failure,
                          'container-create '
                          '--image test-image '
                          '--bay test-bay',
                          self._bay_status_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.delete')
    def test_container_delete_success(self, mock_delete):
        self._test_arg_success('container-delete xxx')
        self.assertTrue(mock_delete.called)
        self.assertEqual(1, mock_delete.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.delete')
    def test_container_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('container-delete xxx xyz')
        self.assertTrue(mock_delete.called)
        self.assertEqual(2, mock_delete.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.delete')
    def test_container_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('container-delete', self._few_argument_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.get')
    def test_container_show_success(self, mock_show):
        self._test_arg_success('container-show xxx')
        self.assertTrue(mock_show.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.get')
    def test_container_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('container-show', self._few_argument_error)
        self.assertFalse(mock_show.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.reboot')
    def test_container_reboot_success(self, mock_reboot):
        self._test_arg_success('container-reboot xxx')
        self.assertTrue(mock_reboot.called)
        self.assertEqual(1, mock_reboot.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.reboot')
    def test_container_reboot_multiple_id_success(self, mock_reboot):
        self._test_arg_success('container-reboot xxx xyz')
        self.assertTrue(mock_reboot.called)
        self.assertEqual(2, mock_reboot.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.reboot')
    def test_container_reboot_failure_no_arg(self, mock_reboot):
        self._test_arg_failure('container-reboot', self._few_argument_error)
        self.assertFalse(mock_reboot.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.stop')
    def test_container_stop_success(self, mock_stop):
        self._test_arg_success('container-stop xxx')
        self.assertTrue(mock_stop.called)
        self.assertEqual(1, mock_stop.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.stop')
    def test_container_stop_multiple_id_success(self, mock_stop):
        self._test_arg_success('container-stop xxx xyz')
        self.assertTrue(mock_stop.called)
        self.assertEqual(2, mock_stop.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.stop')
    def test_container_stop_failure_no_arg(self, mock_stop):
        self._test_arg_failure('container-stop', self._few_argument_error)
        self.assertFalse(mock_stop.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.start')
    def test_container_start_success(self, mock_start):
        self._test_arg_success('container-start xxx')
        self.assertTrue(mock_start.called)
        self.assertEqual(1, mock_start.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.start')
    def test_container_start_multiple_id_success(self, mock_start):
        self._test_arg_success('container-start xxx xyz')
        self.assertTrue(mock_start.called)
        self.assertEqual(2, mock_start.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.start')
    def test_container_start_failure_no_arg(self, mock_start):
        self._test_arg_failure('container-start', self._few_argument_error)
        self.assertFalse(mock_start.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.pause')
    def test_container_pause_success(self, mock_pause):
        self._test_arg_success('container-pause xxx')
        self.assertTrue(mock_pause.called)
        self.assertEqual(1, mock_pause.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.pause')
    def test_container_multiple_id_pause_success(self, mock_pause):
        self._test_arg_success('container-pause xxx xyz')
        self.assertTrue(mock_pause.called)
        self.assertEqual(2, mock_pause.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.pause')
    def test_container_pause_failure_no_arg(self, mock_pause):
        self._test_arg_failure('container-pause', self._few_argument_error)
        self.assertFalse(mock_pause.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.unpause')
    def test_container_unpause_success(self, mock_unpause):
        self._test_arg_success('container-unpause xxx')
        self.assertTrue(mock_unpause.called)
        self.assertEqual(1, mock_unpause.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.unpause')
    def test_container_unpause_multiple_id_success(self, mock_unpause):
        self._test_arg_success('container-unpause xxx xyz')
        self.assertTrue(mock_unpause.called)
        self.assertEqual(2, mock_unpause.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.unpause')
    def test_container_unpause_failure_no_arg(self, mock_unpause):
        self._test_arg_failure('container-unpause', self._few_argument_error)
        self.assertFalse(mock_unpause.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.logs')
    def test_container_logs_success(self, mock_logs):
        self._test_arg_success('container-logs xxx')
        self.assertTrue(mock_logs.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.logs')
    def test_container_logs_failure_no_arg(self, mock_logs):
        self._test_arg_failure('container-logs', self._few_argument_error)
        self.assertFalse(mock_logs.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.execute')
    def test_container_execute_success(self, mock_execute):
        self._test_arg_success('container-exec xxx '
                               '--command ls')
        self.assertTrue(mock_execute.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.execute')
    def test_container_execute_failure_no_option(self, mock_execute):
        self._test_arg_failure('container-exec xxx',
                               self._mandatory_arg_error)
        self.assertFalse(mock_execute.called)

        self._test_arg_failure('container-exec --command ls',
                               self._few_argument_error)
        self.assertFalse(mock_execute.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.execute')
    def test_container_execute_failure_no_arg(self, mock_execute):
        self._test_arg_failure('container-exec', self._few_argument_error)
        self.assertFalse(mock_execute.called)
