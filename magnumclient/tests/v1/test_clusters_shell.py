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
from magnumclient.tests.v1 import test_clustertemplates_shell
from magnumclient.v1.clusters import Cluster


class FakeCluster(Cluster):
    def __init__(self, manager=None, info={}, **kwargs):
        Cluster.__init__(self, manager=manager, info=info)
        self.uuid = kwargs.get('uuid', 'x')
        self.name = kwargs.get('name', 'x')
        self.cluster_template_id = kwargs.get('cluster_template_id', 'x')
        self.stack_id = kwargs.get('stack_id', 'x')
        self.status = kwargs.get('status', 'x')
        self.master_count = kwargs.get('master_count', 1)
        self.node_count = kwargs.get('node_count', 1)
        self.links = kwargs.get('links', [])
        self.create_timeout = kwargs.get('create_timeout', 60)


class ShellTest(shell_test_base.TestCommandLineArgument):

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_success(self, mock_list):
        self._test_arg_success('cluster-list')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_success_with_arg(self, mock_list):
        self._test_arg_success('cluster-list '
                               '--marker some_uuid '
                               '--limit 1 '
                               '--sort-dir asc '
                               '--sort-key uuid')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_ignored_duplicated_field(self, mock_list):
        mock_list.return_value = [FakeCluster()]
        self._test_arg_success(
            'cluster-list --fields status,status,status,name',
            keyword=('\n| uuid | name | node_count | '
                     'master_count | status |\n'))
        # Output should be
        # +------+------+------------+--------------+--------+
        # | uuid | name | node_count | master_count | status |
        # +------+------+------------+--------------+--------+
        # | x    | x    | x          | x            | x      |
        # +------+------+------------+--------------+--------+
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_failure_with_invalid_field(self, mock_list):
        mock_list.return_value = [FakeCluster()]
        _error_msg = [".*?^Non-existent fields are specified: ['xxx','zzz']"]
        self.assertRaises(exceptions.CommandError,
                          self._test_arg_failure,
                          'cluster-list --fields xxx,stack_id,zzz,status',
                          _error_msg)
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_failure_invalid_arg(self, mock_list):
        _error_msg = [
            '.*?^usage: magnum cluster-list ',
            '.*?^error: argument --sort-dir: invalid choice: ',
            ".*?^Try 'magnum help cluster-list' for more information."
            ]
        self._test_arg_failure('cluster-list --sort-dir aaa', _error_msg)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.list')
    def test_cluster_list_failure(self, mock_list):
        self._test_arg_failure('cluster-list --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_success(self, mock_create, mock_get):
        self._test_arg_success('cluster-create --name test '
                               '--cluster-template xxx '
                               '--node-count 123 --timeout 15')
        self.assertTrue(mock_create.called)

        self._test_arg_success('cluster-create --cluster-template xxx')
        self.assertTrue(mock_create.called)

        self._test_arg_success('cluster-create --name test '
                               '--cluster-template xxx')
        self.assertTrue(mock_create.called)

        self._test_arg_success('cluster-create --cluster-template xxx '
                               '--node-count 123')
        self.assertTrue(mock_create.called)

        self._test_arg_success('cluster-create --cluster-template xxx '
                               '--node-count 123 --master-count 123')
        self.assertTrue(mock_create.called)

        self._test_arg_success('cluster-create --cluster-template xxx '
                               '--timeout 15')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_show_clustertemplate_metadata(self,
                                                   mock_cluster,
                                                   mock_clustertemplate):
        mock_cluster.return_value = FakeCluster(info={'links': 0,
                                                      'baymodel_id': 0})
        mock_clustertemplate.return_value = \
            test_clustertemplates_shell.FakeClusterTemplate(info={'links': 0,
                                                                  'uuid': 0,
                                                                  'id': 0,
                                                                  'name': ''})

        self._test_arg_success('cluster-show --long x', 'clustertemplate_name')
        self.assertTrue(mock_cluster.called)
        self.assertTrue(mock_clustertemplate.called)

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_success_only_clustertemplate_arg(self,
                                                             mock_create,
                                                             mock_get):
        self._test_arg_success('cluster-create --cluster-template xxx')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_only_name(self, mock_create):
        self._test_arg_failure('cluster-create --name test',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_only_node_count(self, mock_create):
        self._test_arg_failure('cluster-create --node-count 1',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_invalid_node_count(self, mock_create):
        self._test_arg_failure('cluster-create --cluster-template xxx '
                               '--node-count test',
                               self._invalid_value_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_only_cluster_create_timeout(self,
                                                                mock_create):
        self._test_arg_failure('cluster-create --timeout 15',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_no_arg(self, mock_create):
        self._test_arg_failure('cluster-create',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.create')
    def test_cluster_create_failure_invalid_master_count(self, mock_create):
        self._test_arg_failure('cluster-create --cluster-template xxx '
                               '--master-count test',
                               self._invalid_value_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.delete')
    def test_cluster_delete_success(self, mock_delete):
        self._test_arg_success('cluster-delete xxx')
        self.assertTrue(mock_delete.called)
        self.assertEqual(1, mock_delete.call_count)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.delete')
    def test_cluster_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('cluster-delete xxx xyz')
        self.assertTrue(mock_delete.called)
        self.assertEqual(2, mock_delete.call_count)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.delete')
    def test_cluster_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('cluster-delete', self._few_argument_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_show_success(self, mock_show):
        self._test_arg_success('cluster-show xxx')
        self.assertTrue(mock_show.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('cluster-show', self._few_argument_error)
        self.assertFalse(mock_show.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_success(self, mock_update):
        self._test_arg_success('cluster-update test add test=test')
        self.assertTrue(mock_update.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_success_many_attribute(self, mock_update):
        self._test_arg_success('cluster-update test add test=test test1=test1')
        self.assertTrue(mock_update.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_failure_wrong_op(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum cluster-update ',
            '.*?^error: argument <op>: invalid choice: ',
            ".*?^Try 'magnum help cluster-update' for more information."
            ]
        self._test_arg_failure('cluster-update test wrong test=test',
                               _error_msg)
        self.assertFalse(mock_update.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_failure_wrong_attribute(self, mock_update):
        _error_msg = [
            '.*?^ERROR: Attributes must be a list of PATH=VALUE'
            ]
        self.assertRaises(exceptions.CommandError, self._test_arg_failure,
                          'cluster-update test add test', _error_msg)
        self.assertFalse(mock_update.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.update')
    def test_cluster_update_failure_few_args(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum cluster-update ',
            '.*?^error: (the following arguments|too few arguments)',
            ".*?^Try 'magnum help cluster-update' for more information."
            ]
        self._test_arg_failure('cluster-update', _error_msg)
        self.assertFalse(mock_update.called)

        self._test_arg_failure('cluster-update test', _error_msg)
        self.assertFalse(mock_update.called)

        self._test_arg_failure('cluster-update test add', _error_msg)
        self.assertFalse(mock_update.called)

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_config_success(self, mock_cluster, mock_clustertemplate):
        mock_cluster.return_value = FakeCluster(status='UPDATE_COMPLETE')
        self._test_arg_success('cluster-config xxx')
        self.assertTrue(mock_cluster.called)

        mock_cluster.return_value = FakeCluster(status='CREATE_COMPLETE')
        self._test_arg_success('cluster-config xxx')
        self.assertTrue(mock_cluster.called)

        self._test_arg_success('cluster-config --dir /tmp xxx')
        self.assertTrue(mock_cluster.called)

        self._test_arg_success('cluster-config --force xxx')
        self.assertTrue(mock_cluster.called)

        self._test_arg_success('cluster-config --dir /tmp --force xxx')
        self.assertTrue(mock_cluster.called)

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
        self.assertFalse(mock_cluster.called)

    @mock.patch('magnumclient.v1.clusters.ClusterManager.get')
    def test_cluster_config_failure_wrong_arg(self, mock_cluster):
        self._test_arg_failure('cluster-config xxx yyy',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_cluster.called)
