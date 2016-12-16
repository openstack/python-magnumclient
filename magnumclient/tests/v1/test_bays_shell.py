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


class FakeCert(object):
    def __init__(self, pem):
        self.pem = pem


class ShellTest(shell_test_base.TestCommandLineArgument):

    def _get_expected_args_list(self, marker=None, limit=None,
                                sort_dir=None, sort_key=None):
        expected_args = {}
        expected_args['marker'] = marker
        expected_args['limit'] = limit
        expected_args['sort_dir'] = sort_dir
        expected_args['sort_key'] = sort_key

        return expected_args

    def _get_expected_args_create(self, baymodel_id, name=None,
                                  master_count=1, node_count=1,
                                  bay_create_timeout=60,
                                  discovery_url=None):
        expected_args = {}
        expected_args['name'] = name
        expected_args['baymodel_id'] = baymodel_id
        expected_args['master_count'] = master_count
        expected_args['node_count'] = node_count
        expected_args['bay_create_timeout'] = bay_create_timeout
        expected_args['discovery_url'] = discovery_url

        return expected_args

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_success(self, mock_list):
        self._test_arg_success('bay-list')
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_success_with_arg(self, mock_list):
        self._test_arg_success('bay-list '
                               '--marker some_uuid '
                               '--limit 1 '
                               '--sort-dir asc '
                               '--sort-key uuid')
        expected_args = self._get_expected_args_list('some_uuid', 1,
                                                     'asc', 'uuid')
        mock_list.assert_called_once_with(**expected_args)

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
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_failure_with_invalid_field(self, mock_list):
        mock_list.return_value = [FakeBay()]
        _error_msg = [".*?^Non-existent fields are specified: ['xxx','zzz']"]
        self.assertRaises(exceptions.CommandError,
                          self._test_arg_failure,
                          'bay-list --fields xxx,stack_id,zzz,status',
                          _error_msg)
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_failure_invalid_arg(self, mock_list):
        _error_msg = [
            '.*?^usage: magnum bay-list ',
            '.*?^error: argument --sort-dir: invalid choice: ',
            ".*?^Try 'magnum help bay-list' for more information."
            ]
        self._test_arg_failure('bay-list --sort-dir aaa', _error_msg)
        mock_list.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_failure(self, mock_list):
        self._test_arg_failure('bay-list --wrong',
                               self._unrecognized_arg_error)
        mock_list.assert_not_called()

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_success(self, mock_create, mock_get):
        mock_baymodel = mock.MagicMock()
        mock_baymodel.uuid = 'xxx'
        mock_get.return_value = mock_baymodel
        self._test_arg_success('bay-create --name test --baymodel xxx '
                               '--node-count 123 --timeout 15')
        expected_args = self._get_expected_args_create('xxx', name='test',
                                                       node_count=123,
                                                       bay_create_timeout=15)
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('bay-create --baymodel xxx')
        expected_args = self._get_expected_args_create('xxx')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('bay-create --name test --baymodel xxx')
        expected_args = self._get_expected_args_create('xxx',
                                                       name='test')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('bay-create --baymodel xxx --node-count 123')
        expected_args = self._get_expected_args_create('xxx',
                                                       node_count=123)

        self._test_arg_success('bay-create --baymodel xxx --node-count 123 '
                               '--master-count 123')
        expected_args = self._get_expected_args_create('xxx',
                                                       master_count=123,
                                                       node_count=123)
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('bay-create --baymodel xxx '
                               '--timeout 15')
        expected_args = self._get_expected_args_create('xxx',
                                                       bay_create_timeout=15)
        mock_create.assert_called_with(**expected_args)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_show_baymodel_metadata(self, mock_bay, mock_baymodel):
        mock_bay.return_value = mock.MagicMock(baymodel_id=0)
        mock_baymodel.return_value = test_baymodels_shell.FakeBayModel(
            info={'links': 0, 'uuid': 0, 'id': 0, 'name': ''})

        self._test_arg_success('bay-show --long x')
        mock_bay.assert_called_once_with('x')
        mock_baymodel.assert_called_once_with(0)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_success_only_baymodel_arg(self, mock_create, mock_get):
        mock_baymodel = mock.MagicMock()
        mock_baymodel.uuid = 'xxx'
        mock_get.return_value = mock_baymodel
        self._test_arg_success('bay-create --baymodel xxx')
        expected_args = self._get_expected_args_create('xxx')
        mock_create.assert_called_with(**expected_args)

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_only_name(self, mock_create):
        self._test_arg_failure('bay-create --name test',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_only_node_count(self, mock_create):
        self._test_arg_failure('bay-create --node-count 1',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_invalid_node_count(self, mock_create):
        self._test_arg_failure('bay-create --baymodel xxx --node-count test',
                               self._invalid_value_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_only_bay_create_timeout(self, mock_create):
        self._test_arg_failure('bay-create --timeout 15',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_no_arg(self, mock_create):
        self._test_arg_failure('bay-create',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_invalid_master_count(self, mock_create):
        self._test_arg_failure('bay-create --baymodel xxx --master-count test',
                               self._invalid_value_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.delete')
    def test_bay_delete_success(self, mock_delete):
        self._test_arg_success('bay-delete xxx')
        mock_delete.assert_called_once_with('xxx')

    @mock.patch('magnumclient.v1.bays.BayManager.delete')
    def test_bay_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('bay-delete xxx xyz')
        calls = [mock.call('xxx'), mock.call('xyz')]
        mock_delete.assert_has_calls(calls)

    @mock.patch('magnumclient.v1.bays.BayManager.delete')
    def test_bay_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('bay-delete', self._few_argument_error)
        mock_delete.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_show_success(self, mock_show):
        self._test_arg_success('bay-show xxx')
        mock_show.assert_called_once_with('xxx')

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('bay-show', self._few_argument_error)
        mock_show.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_success(self, mock_update):
        self._test_arg_success('bay-update test add test=test')
        patch = [{'op': 'add', 'path': '/test', 'value': 'test'}]
        mock_update.assert_called_once_with('test', patch, False)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_success_many_attribute(self, mock_update):
        self._test_arg_success('bay-update test add test=test test1=test1')
        patch = [{'op': 'add', 'path': '/test', 'value': 'test'},
                 {'op': 'add', 'path': '/test1', 'value': 'test1'}]
        mock_update.assert_called_once_with('test', patch, False)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_success_rollback(self, mock_update):
        self._test_arg_success('bay-update test add test=test --rollback')
        patch = [{'op': 'add', 'path': '/test', 'value': 'test'}]
        mock_update.assert_called_once_with('test', patch, True)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_rollback_old_api_version(self, mock_update):
        self.assertRaises(
            exceptions.CommandError,
            self.shell,
            '--magnum-api-version 1.2 bay-update '
            'test add test=test --rollback')
        mock_update.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_failure_wrong_op(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum bay-update ',
            '.*?^error: argument <op>: invalid choice: ',
            ".*?^Try 'magnum help bay-update' for more information."
            ]
        self._test_arg_failure('bay-update test wrong test=test', _error_msg)
        mock_update.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_failure_wrong_attribute(self, mock_update):
        _error_msg = [
            '.*?^ERROR: Attributes must be a list of PATH=VALUE'
            ]
        self.assertRaises(exceptions.CommandError, self._test_arg_failure,
                          'bay-update test add test', _error_msg)
        mock_update.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_failure_few_args(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum bay-update ',
            '.*?^error: (the following arguments|too few arguments)',
            ".*?^Try 'magnum help bay-update' for more information."
            ]
        self._test_arg_failure('bay-update', _error_msg)
        mock_update.assert_not_called()

        self._test_arg_failure('bay-update test', _error_msg)
        mock_update.assert_not_called()

        self._test_arg_failure('bay-update test add', _error_msg)
        mock_update.assert_not_called()

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_config_success(self, mock_bay, mock_baymodel):
        mock_bay.return_value = FakeBay(status='UPDATE_COMPLETE')
        self._test_arg_success('bay-config xxx')
        mock_bay.assert_called_with('xxx')

        mock_bay.return_value = FakeBay(status='CREATE_COMPLETE')
        self._test_arg_success('bay-config xxx')
        mock_bay.assert_called_with('xxx')

        self._test_arg_success('bay-config --dir /tmp xxx')
        mock_bay.assert_called_with('xxx')

        self._test_arg_success('bay-config --force xxx')
        mock_bay.assert_called_with('xxx')

        self._test_arg_success('bay-config --dir /tmp --force xxx')
        mock_bay.assert_called_with('xxx')

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
        mock_bay.assert_not_called()

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_config_failure_wrong_arg(self, mock_bay):
        self._test_arg_failure('bay-config xxx yyy',
                               self._unrecognized_arg_error)
        mock_bay.assert_not_called()

    @mock.patch('os.path.exists')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.create')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.get')
    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def _test_bay_config_success(self, mock_bay, mock_bm, mock_cert_get,
                                 mock_cert_create, mock_exists, coe, shell,
                                 tls_disable):
        cert = FakeCert(pem='foo bar')
        mock_exists.return_value = False
        mock_bay.return_value = FakeBay(status='CREATE_COMPLETE',
                                        info={'name': 'Kluster',
                                              'api_address': '127.0.0.1'},
                                        baymodel_id='fake_bm',
                                        uuid='fake_bay')
        mock_cert_get.return_value = cert
        mock_cert_create.return_value = cert
        mock_bm.return_value = test_baymodels_shell. \
            FakeBayModel(coe=coe, name='fake_bm', tls_disabled=tls_disable)
        with mock.patch.dict('os.environ', {'SHELL': shell}):
            self._test_arg_success('bay-config test_bay')

        self.assertTrue(mock_exists.called)
        mock_bay.assert_called_once_with('test_bay')
        mock_bm.assert_called_once_with('fake_bm')
        if not tls_disable:
            mock_cert_create.assert_called_once_with(cluster_uuid='fake_bay',
                                                     csr=mock.ANY)
            mock_cert_get.assert_called_once_with(cluster_uuid='fake_bay')

    def test_bay_config_swarm_success_with_tls_csh(self):
        self._test_bay_config_success(coe='swarm', shell='csh',
                                      tls_disable=False)

    def test_bay_config_swarm_success_with_tls_non_csh(self):
        self._test_bay_config_success(coe='swarm', shell='zsh',
                                      tls_disable=False)

    def test_bay_config_swarm_success_without_tls_csh(self):
        self._test_bay_config_success(coe='swarm', shell='csh',
                                      tls_disable=True)

    def test_bay_config_swarm_success_without_tls_non_csh(self):
        self._test_bay_config_success(coe='swarm', shell='zsh',
                                      tls_disable=True)

    def test_bay_config_k8s_success_with_tls_csh(self):
        self._test_bay_config_success(coe='kubernetes', shell='csh',
                                      tls_disable=False)

    def test_bay_config_k8s_success_with_tls_non_csh(self):
        self._test_bay_config_success(coe='kubernetes', shell='zsh',
                                      tls_disable=False)

    def test_bay_config_k8s_success_without_tls_csh(self):
        self._test_bay_config_success(coe='kubernetes', shell='csh',
                                      tls_disable=True)

    def test_bay_config_k8s_success_without_tls_non_csh(self):
        self._test_bay_config_success(coe='kubernetes', shell='zsh',
                                      tls_disable=True)
