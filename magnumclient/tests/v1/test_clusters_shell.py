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

from magnumclient.common import cliutils
from magnumclient import exceptions
from magnumclient.tests.v1 import shell_test_base
from magnumclient.tests.v1 import test_clustertemplates_shell
from magnumclient.v1.clusters import Cluster


class FakeCluster(Cluster):
    def __init__(self, manager=None, info={}, **kwargs):
        Cluster.__init__(self, manager=manager, info=info)
        self.uuid = kwargs.get('uuid', 'x')
        self.keypair = kwargs.get('keypair', 'x')
        self.name = kwargs.get('name', 'x')
        self.cluster_template_id = kwargs.get('cluster_template_id', 'x')
        self.stack_id = kwargs.get('stack_id', 'x')
        self.status = kwargs.get('status', 'x')
        self.master_count = kwargs.get('master_count', 1)
        self.node_count = kwargs.get('node_count', 1)
        self.links = kwargs.get('links', [])
        self.create_timeout = kwargs.get('create_timeout', 60)


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

    def _get_expected_args_create(self, cluster_template_id, name=None,
                                  master_count=1, node_count=1,
                                  create_timeout=60, keypair=None,
                                  discovery_url=None):
        expected_args = {}
        expected_args['name'] = name
        expected_args['cluster_template_id'] = cluster_template_id
        expected_args['master_count'] = master_count
        expected_args['node_count'] = node_count
        expected_args['create_timeout'] = create_timeout
        expected_args['discovery_url'] = discovery_url
        expected_args['keypair'] = keypair

        return expected_args

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_success(self, mock_list):
        self._test_arg_success('cluster-list')
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_success_with_arg(self, mock_list):
        self._test_arg_success('cluster-list '
                               '--marker some_uuid '
                               '--limit 1 '
                               '--sort-dir asc '
                               '--sort-key uuid')
        expected_args = self._get_expected_args_list('some_uuid', 1,
                                                     'asc', 'uuid')
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_ignored_duplicated_field(self, mock_list):
        mock_list.return_value = [FakeCluster()]
        self._test_arg_success(
            'cluster-list --fields status,status,status,name',
            keyword=('\n| uuid | name | keypair | node_count | '
                     'master_count | status |\n'))
        # Output should be
        # +------+------+---------+--------------+--------------+--------+
        # | uuid | name | keypair | node_count   | master_count | status |
        # +------+------+---------+--------------+--------------+--------+
        # | x    | x    | x       | x            | x            | x      |
        # +------+------+---------+--------------+--------------+--------+
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_failure_with_invalid_field(self, mock_list):
        mock_list.return_value = [FakeCluster()]
        _error_msg = [".*?^Non-existent fields are specified: ['xxx','zzz']"]
        self.assertRaises(exceptions.CommandError,
                          self._test_arg_failure,
                          'cluster-list --fields xxx,stack_id,zzz,status',
                          _error_msg)
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_failure_invalid_arg(self, mock_list):
        _error_msg = [
            '.*?^usage: magnum cluster-list ',
            '.*?^error: argument --sort-dir: invalid choice: ',
            ".*?^Try 'magnum help cluster-list' for more information."
            ]
        self._test_arg_failure('cluster-list --sort-dir aaa', _error_msg)
        mock_list.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_failure(self, mock_list):
        self._test_arg_failure('cluster-list --wrong',
                               self._unrecognized_arg_error)
        mock_list.assert_not_called()

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_success(self, mock_create, mock_get):
        mock_ct = mock.MagicMock()
        mock_ct.uuid = 'xxx'
        mock_get.return_value = mock_ct
        self._test_arg_success('cluster-create test '
                               '--cluster-template xxx '
                               '--node-count 123 --timeout 15')
        expected_args = self._get_expected_args_create('xxx', name='test',
                                                       node_count=123,
                                                       create_timeout=15)
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('cluster-create --cluster-template xxx')
        expected_args = self._get_expected_args_create('xxx')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('cluster-create --cluster-template xxx '
                               '--keypair x')
        expected_args = self._get_expected_args_create('xxx',
                                                       keypair='x')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('cluster-create test '
                               '--cluster-template xxx')
        expected_args = self._get_expected_args_create('xxx',
                                                       name='test')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('cluster-create --cluster-template xxx '
                               '--node-count 123')
        expected_args = self._get_expected_args_create('xxx',
                                                       node_count=123)
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('cluster-create --cluster-template xxx '
                               '--node-count 123 --master-count 123')
        expected_args = self._get_expected_args_create('xxx',
                                                       master_count=123,
                                                       node_count=123)
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('cluster-create --cluster-template xxx '
                               '--timeout 15')
        expected_args = self._get_expected_args_create('xxx',
                                                       create_timeout=15)
        mock_create.assert_called_with(**expected_args)

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_deprecation_warnings(self, mock_create,
                                                 mock_get):
        self._test_arg_failure('cluster-create --cluster-template xxx '
                               '--keypair-id x',
                               self._deprecated_warning)
        self.assertTrue(mock_create.called)
        self.assertTrue(mock_get.called)

        self._test_arg_failure('cluster-create --cluster-template xxx '
                               '--name foo ',
                               self._deprecated_warning)
        self.assertTrue(mock_create.called)
        self.assertTrue(mock_get.called)

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_deprecation_errors(self,
                                               mock_create,
                                               mock_get):
        self._test_arg_failure('cluster-create --cluster-template xxx '
                               '--keypair-id x --keypair x',
                               self._too_many_group_arg_error)
        self.assertFalse(mock_create.called)
        self.assertFalse(mock_get.called)

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_show_clustertemplate_metadata(self,
                                                   mock_cluster,
                                                   mock_clustertemplate):
        mock_cluster.return_value = mock.MagicMock(cluster_template_id=0)

        mock_clustertemplate.return_value = \
            test_clustertemplates_shell.FakeClusterTemplate(info={'links': 0,
                                                                  'uuid': 0,
                                                                  'id': 0,
                                                                  'name': ''})

        self._test_arg_success('cluster-show --long x')
        mock_cluster.assert_called_once_with('x')
        mock_clustertemplate.assert_called_once_with(0)

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def _test_cluster_create_success(self, cmd, expected_args, expected_kwargs,
                                     mock_create, mock_get):
        mock_ct = mock.MagicMock()
        mock_ct.uuid = 'xxx'
        mock_get.return_value = mock_ct
        self._test_arg_success(cmd)
        expected = self._get_expected_args_create(*expected_args,
                                                  **expected_kwargs)
        mock_create.assert_called_with(**expected)

    def test_cluster_create_success_only_clustertemplate_arg(self):
        self._test_cluster_create_success(
            'cluster-create --cluster-template xxx',
            ['xxx'],
            {})

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_success_only_positional_name(self,
                                                         mock_create,
                                                         mock_get):
        self._test_cluster_create_success(
            'cluster-create foo --cluster-template xxx',
            ['xxx'],
            {'name': 'foo'})

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_success_only_optional_name(self,
                                                       mock_create,
                                                       mock_get):
        self._test_cluster_create_success(
            'cluster-create --name foo --cluster-template xxx',
            ['xxx'],
            {'name': 'foo'})

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_only_name(self, mock_create):
        self._test_arg_failure('cluster-create --name test',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_only_keypair(self, mock_create):
        self._test_arg_failure('cluster-create --keypair test',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_only_node_count(self, mock_create):
        self._test_arg_failure('cluster-create --node-count 1',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_invalid_node_count(self, mock_create):
        self._test_arg_failure('cluster-create --cluster-template xxx '
                               '--node-count test',
                               self._invalid_value_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_only_cluster_create_timeout(self,
                                                                mock_create):
        self._test_arg_failure('cluster-create --timeout 15',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_no_arg(self, mock_create):
        self._test_arg_failure('cluster-create',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_invalid_master_count(self, mock_create):
        self._test_arg_failure('cluster-create --cluster-template xxx '
                               '--master-count test',
                               self._invalid_value_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_duplicate_name(self, mock_create):
        self.assertRaises(cliutils.DuplicateArgs,
                          self._test_arg_failure,
                          'cluster-create foo --name bar '
                          '--cluster-template xxx',
                          self._duplicate_name_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.delete')
    def test_cluster_delete_success(self, mock_delete):
        self._test_arg_success('cluster-delete xxx')
        mock_delete.assert_called_once_with('xxx')

    @mock.patch('magnumclient.v1.clusters.ClusterManager.delete')
    def test_cluster_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('cluster-delete xxx xyz')
        calls = [mock.call('xxx'), mock.call('xyz')]
        mock_delete.assert_has_calls(calls)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.delete')
    def test_cluster_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('cluster-delete', self._few_argument_error)
        mock_delete.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_show_success(self, mock_show):
        self._test_arg_success('cluster-show xxx')
        mock_show.assert_called_once_with('xxx')

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('cluster-show', self._few_argument_error)
        mock_show.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_success(self, mock_update):
        self._test_arg_success('cluster-update test add test=test')
        patch = [{'op': 'add', 'path': '/test', 'value': 'test'}]
        mock_update.assert_called_once_with('test', patch, False)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_success_many_attribute(self, mock_update):
        self._test_arg_success('cluster-update test add test=test test1=test1')
        patch = [{'op': 'add', 'path': '/test', 'value': 'test'},
                 {'op': 'add', 'path': '/test1', 'value': 'test1'}]
        mock_update.assert_called_once_with('test', patch, False)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_success_rollback(self, mock_update):
        self._test_arg_success('cluster-update test add test=test --rollback')
        patch = [{'op': 'add', 'path': '/test', 'value': 'test'}]
        mock_update.assert_called_once_with('test', patch, True)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_rollback_old_api_version(self, mock_update):
        self.assertRaises(
            exceptions.CommandError,
            self.shell,
            '--magnum-api-version 1.2 cluster-update '
            'test add test=test --rollback')
        mock_update.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_failure_wrong_op(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum cluster-update ',
            '.*?^error: argument <op>: invalid choice: ',
            ".*?^Try 'magnum help cluster-update' for more information."
            ]
        self._test_arg_failure('cluster-update test wrong test=test',
                               _error_msg)
        mock_update.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_failure_wrong_attribute(self, mock_update):
        _error_msg = [
            '.*?^ERROR: Attributes must be a list of PATH=VALUE'
            ]
        self.assertRaises(exceptions.CommandError, self._test_arg_failure,
                          'cluster-update test add test', _error_msg)
        mock_update.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_failure_few_args(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum cluster-update ',
            '.*?^error: (the following arguments|too few arguments)',
            ".*?^Try 'magnum help cluster-update' for more information."
            ]
        self._test_arg_failure('cluster-update', _error_msg)
        mock_update.assert_not_called()

        self._test_arg_failure('cluster-update test', _error_msg)
        mock_update.assert_not_called()

        self._test_arg_failure('cluster-update test add', _error_msg)
        mock_update.assert_not_called()

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_config_success(self, mock_cluster, mock_clustertemplate):
        mock_cluster.return_value = FakeCluster(status='UPDATE_COMPLETE')
        self._test_arg_success('cluster-config xxx')
        mock_cluster.assert_called_with('xxx')

        mock_cluster.return_value = FakeCluster(status='CREATE_COMPLETE')
        self._test_arg_success('cluster-config xxx')
        mock_cluster.assert_called_with('xxx')

        self._test_arg_success('cluster-config --dir /tmp xxx')
        mock_cluster.assert_called_with('xxx')

        self._test_arg_success('cluster-config --force xxx')
        mock_cluster.assert_called_with('xxx')

        self._test_arg_success('cluster-config --dir /tmp --force xxx')
        mock_cluster.assert_called_with('xxx')

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_config_failure_wrong_status(self,
                                                 mock_cluster,
                                                 mock_clustertemplate):
        mock_cluster.return_value = FakeCluster(status='CREATE_IN_PROGRESS')
        self.assertRaises(exceptions.CommandError,
                          self._test_arg_failure,
                          'cluster-config xxx',
                          ['.*?^Cluster in status: '])

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_config_failure_no_arg(self, mock_cluster):
        self._test_arg_failure('cluster-config', self._few_argument_error)
        mock_cluster.assert_not_called()

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_config_failure_wrong_arg(self, mock_cluster):
        self._test_arg_failure('cluster-config xxx yyy',
                               self._unrecognized_arg_error)
        mock_cluster.assert_not_called()

    @mock.patch('os.path.exists')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.create')
    @mock.patch('magnumclient.v1.certificates.CertificateManager.get')
    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def _test_cluster_config_success(self, mock_cluster, mock_ct,
                                     mock_cert_get, mock_cert_create,
                                     mock_exists, coe, shell, tls_disable):
        cert = FakeCert(pem='foo bar')
        mock_exists.return_value = False
        mock_cluster.return_value = FakeCluster(status='CREATE_COMPLETE',
                                                info={
                                                    'name': 'Kluster',
                                                    'api_address': '10.0.0.1'},
                                                cluster_template_id='fake_ct',
                                                uuid='fake_cluster')
        mock_cert_get.return_value = cert
        mock_cert_create.return_value = cert
        mock_ct.return_value = test_clustertemplates_shell.\
            FakeClusterTemplate(coe=coe, name='fake_ct',
                                tls_disabled=tls_disable)
        with mock.patch.dict('os.environ', {'SHELL': shell}):
            self._test_arg_success('cluster-config test_cluster')

        self.assertTrue(mock_exists.called)
        mock_cluster.assert_called_once_with('test_cluster')
        mock_ct.assert_called_once_with('fake_ct')
        if not tls_disable:
            mock_cert_create.assert_called_once_with(
                cluster_uuid='fake_cluster', csr=mock.ANY)
            mock_cert_get.assert_called_once_with(cluster_uuid='fake_cluster')

    def test_cluster_config_swarm_success_with_tls_csh(self):
        self._test_cluster_config_success(coe='swarm', shell='csh',
                                          tls_disable=False)

    def test_cluster_config_swarm_success_with_tls_non_csh(self):
        self._test_cluster_config_success(coe='swarm', shell='zsh',
                                          tls_disable=False)

    def test_cluster_config_swarm_success_without_tls_csh(self):
        self._test_cluster_config_success(coe='swarm', shell='csh',
                                          tls_disable=True)

    def test_cluster_config_swarm_success_without_tls_non_csh(self):
        self._test_cluster_config_success(coe='swarm', shell='zsh',
                                          tls_disable=True)

    def test_cluster_config_k8s_success_with_tls_csh(self):
        self._test_cluster_config_success(coe='kubernetes', shell='csh',
                                          tls_disable=False)

    def test_cluster_config_k8s_success_with_tls_non_csh(self):
        self._test_cluster_config_success(coe='kubernetes', shell='zsh',
                                          tls_disable=False)

    def test_cluster_config_k8s_success_without_tls_csh(self):
        self._test_cluster_config_success(coe='kubernetes', shell='csh',
                                          tls_disable=True)

    def test_cluster_config_k8s_success_without_tls_non_csh(self):
        self._test_cluster_config_success(coe='kubernetes', shell='zsh',
                                          tls_disable=True)
