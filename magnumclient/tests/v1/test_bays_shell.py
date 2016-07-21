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
from magnumclient.tests.v1 import test_baymodels_shell
from magnumclient.v1.bays import Bay


class FakeBay(Bay):
    def __init__(self, manager=None, info={}, **kwargs):
        Bay.__init__(self, manager=manager, info=info)
        self.uuid = kwargs.get('uuid', 'x')
        self.name = kwargs.get('name', 'x')
        self.baymodel_id = kwargs.get('baymodel_id', 'x')
        self.stack_id = kwargs.get('stack_id', 'x')
        self.status = kwargs.get('status', 'x')
        self.master_count = kwargs.get('master_count', 1)
        self.node_count = kwargs.get('node_count', 1)
        self.links = kwargs.get('links', [])
        self.bay_create_timeout = kwargs.get('bay_create_timeout', 60)


class ShellTest(shell_test_base.TestCommandLineArgument):

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_success(self, mock_list):
        self._test_arg_success('bay-list')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_success_with_arg(self, mock_list):
        self._test_arg_success('bay-list '
                               '--marker some_uuid '
                               '--limit 1 '
                               '--sort-dir asc '
                               '--sort-key uuid')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_ignored_duplicated_field(self, mock_list):
        mock_list.return_value = [FakeBay()]
        self._test_arg_success('bay-list --fields status,status,status,name',
                               keyword=('\n| uuid | name | node_count | '
                                        'master_count | status |\n'))
        # Output should be
        # +------+------+------------+--------------+--------+
        # | uuid | name | node_count | master_count | status |
        # +------+------+------------+--------------+--------+
        # | x    | x    | x          | x            | x      |
        # +------+------+------------+--------------+--------+
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_failure_with_invalid_field(self, mock_list):
        mock_list.return_value = [FakeBay()]
        _error_msg = [".*?^Non-existent fields are specified: ['xxx','zzz']"]
        self.assertRaises(exceptions.CommandError,
                          self._test_arg_failure,
                          'bay-list --fields xxx,stack_id,zzz,status',
                          _error_msg)
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_failure_invalid_arg(self, mock_list):
        _error_msg = [
            '.*?^usage: magnum bay-list ',
            '.*?^error: argument --sort-dir: invalid choice: ',
            ".*?^Try 'magnum help bay-list' for more information."
            ]
        self._test_arg_failure('bay-list --sort-dir aaa', _error_msg)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_failure(self, mock_list):
        self._test_arg_failure('bay-list --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_success(self, mock_create, mock_get):
        self._test_arg_success('bay-create --name test --baymodel xxx '
                               '--node-count 123 --timeout 15')
        self.assertTrue(mock_create.called)

        self._test_arg_success('bay-create --baymodel xxx')
        self.assertTrue(mock_create.called)

        self._test_arg_success('bay-create --name test --baymodel xxx')
        self.assertTrue(mock_create.called)

        self._test_arg_success('bay-create --baymodel xxx --node-count 123')
        self.assertTrue(mock_create.called)

        self._test_arg_success('bay-create --baymodel xxx --node-count 123 '
                               '--master-count 123')
        self.assertTrue(mock_create.called)

        self._test_arg_success('bay-create --baymodel xxx '
                               '--timeout 15')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_show_baymodel_metadata(self, mock_bay, mock_baymodel):
        mock_bay.return_value = FakeBay(info={'links': 0, 'baymodel_id': 0})
        mock_baymodel.return_value = test_baymodels_shell.FakeBayModel(
            info={'links': 0, 'uuid': 0, 'id': 0, 'name': ''})

        self._test_arg_success('bay-show --long x', 'baymodel_name')
        self.assertTrue(mock_bay.called)
        self.assertTrue(mock_baymodel.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_success_only_baymodel_arg(self, mock_create, mock_get):
        self._test_arg_success('bay-create --baymodel xxx')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_only_name(self, mock_create):
        self._test_arg_failure('bay-create --name test',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_only_node_count(self, mock_create):
        self._test_arg_failure('bay-create --node-count 1',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_invalid_node_count(self, mock_create):
        self._test_arg_failure('bay-create --baymodel xxx --node-count test',
                               self._invalid_value_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_only_bay_create_timeout(self, mock_create):
        self._test_arg_failure('bay-create --timeout 15',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_no_arg(self, mock_create):
        self._test_arg_failure('bay-create',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_invalid_master_count(self, mock_create):
        self._test_arg_failure('bay-create --baymodel xxx --master-count test',
                               self._invalid_value_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.delete')
    def test_bay_delete_success(self, mock_delete):
        self._test_arg_success('bay-delete xxx')
        self.assertTrue(mock_delete.called)
        self.assertEqual(1, mock_delete.call_count)

    @mock.patch('magnumclient.v1.bays.BayManager.delete')
    def test_bay_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('bay-delete xxx xyz')
        self.assertTrue(mock_delete.called)
        self.assertEqual(2, mock_delete.call_count)

    @mock.patch('magnumclient.v1.bays.BayManager.delete')
    def test_bay_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('bay-delete', self._few_argument_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_show_success(self, mock_show):
        self._test_arg_success('bay-show xxx')
        self.assertTrue(mock_show.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('bay-show', self._few_argument_error)
        self.assertFalse(mock_show.called)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_success(self, mock_update):
        self._test_arg_success('bay-update test add test=test')
        self.assertTrue(mock_update.called)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_success_many_attribute(self, mock_update):
        self._test_arg_success('bay-update test add test=test test1=test1')
        self.assertTrue(mock_update.called)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_failure_wrong_op(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum bay-update ',
            '.*?^error: argument <op>: invalid choice: ',
            ".*?^Try 'magnum help bay-update' for more information."
            ]
        self._test_arg_failure('bay-update test wrong test=test', _error_msg)
        self.assertFalse(mock_update.called)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_failure_wrong_attribute(self, mock_update):
        _error_msg = [
            '.*?^ERROR: Attributes must be a list of PATH=VALUE'
            ]
        self.assertRaises(exceptions.CommandError, self._test_arg_failure,
                          'bay-update test add test', _error_msg)
        self.assertFalse(mock_update.called)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_failure_few_args(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum bay-update ',
            '.*?^error: (the following arguments|too few arguments)',
            ".*?^Try 'magnum help bay-update' for more information."
            ]
        self._test_arg_failure('bay-update', _error_msg)
        self.assertFalse(mock_update.called)

        self._test_arg_failure('bay-update test', _error_msg)
        self.assertFalse(mock_update.called)

        self._test_arg_failure('bay-update test add', _error_msg)
        self.assertFalse(mock_update.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_config_success(self, mock_bay, mock_baymodel):
        mock_bay.return_value = FakeBay(status='UPDATE_COMPLETE')
        self._test_arg_success('bay-config xxx')
        self.assertTrue(mock_bay.called)

        mock_bay.return_value = FakeBay(status='CREATE_COMPLETE')
        self._test_arg_success('bay-config xxx')
        self.assertTrue(mock_bay.called)

        self._test_arg_success('bay-config --dir /tmp xxx')
        self.assertTrue(mock_bay.called)

        self._test_arg_success('bay-config --force xxx')
        self.assertTrue(mock_bay.called)

        self._test_arg_success('bay-config --dir /tmp --force xxx')
        self.assertTrue(mock_bay.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_config_failure_wrong_status(self, mock_bay, mock_baymodel):
        mock_bay.return_value = FakeBay(status='CREATE_IN_PROGRESS')
        self.assertRaises(exceptions.CommandError,
                          self._test_arg_failure,
                          'bay-config xxx',
                          ['.*?^Bay in status: '])

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_config_failure_no_arg(self, mock_bay):
        self._test_arg_failure('bay-config', self._few_argument_error)
        self.assertFalse(mock_bay.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_config_failure_wrong_arg(self, mock_bay):
        self._test_arg_failure('bay-config xxx yyy',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_bay.called)
