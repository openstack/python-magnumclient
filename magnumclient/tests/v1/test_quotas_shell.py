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

    def _get_expected_args_list(self, marker=None, limit=None, sort_dir=None,
                                sort_key=None, all_tenants=False):
        expected_args = {}
        expected_args['marker'] = marker
        expected_args['limit'] = limit
        expected_args['sort_dir'] = sort_dir
        expected_args['sort_key'] = sort_key
        expected_args['all_tenants'] = False
        return expected_args

    def _get_expected_args_create(self, project_id, resource, hard_limit):
        expected_args = {}
        expected_args['project_id'] = project_id
        expected_args['resource'] = resource
        expected_args['hard_limit'] = hard_limit
        return expected_args

    @mock.patch('magnumclient.v1.quotas.QuotasManager.list')
    def test_quotas_list_success(self, mock_list):
        self._test_arg_success('quotas-list')
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.quotas.QuotasManager.list')
    def test_quotas_list_failure(self, mock_list):
        self._test_arg_failure('quotas-list --wrong',
                               self._unrecognized_arg_error)
        mock_list.assert_not_called()

    @mock.patch('magnumclient.v1.quotas.QuotasManager.create')
    def test_quotas_create_success(self, mock_create):
        self._test_arg_success('quotas-create --project-id abc '
                               '--resource Cluster '
                               '--hard-limit 15')
        expected_args = self._get_expected_args_create('abc', 'Cluster', 15)
        mock_create.assert_called_with(**expected_args)

    @mock.patch('magnumclient.v1.quotas.QuotasManager.create')
    def test_quotas_create_failure_only_project_id(self, mock_create):
        self._test_arg_failure('quotas-create --project-id abc',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.quotas.QuotasManager.create')
    def test_quotas_create_failure_only_resource(self, mock_create):
        self._test_arg_failure('quotas-create --resource Cluster',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.quotas.QuotasManager.create')
    def test_quotas_create_failure_only_hard_limit(self, mock_create):
        self._test_arg_failure('quotas-create --hard-limit 10',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.quotas.QuotasManager.create')
    def test_quotas_create_failure_no_arg(self, mock_create):
        self._test_arg_failure('quotas-create',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch('magnumclient.v1.quotas.QuotasManager.delete')
    def test_quotas_delete_success(self, mock_delete):
        self._test_arg_success(
            'quotas-delete --project-id xxx --resource Cluster')
        mock_delete.assert_called_once_with('xxx', 'Cluster')

    @mock.patch('magnumclient.v1.quotas.QuotasManager.delete')
    def test_quotas_delete_failure_no_project_id(self, mock_delete):
        self._test_arg_failure('quotas-delete --resource Cluster',
                               self._mandatory_arg_error)
        mock_delete.assert_not_called()

    @mock.patch('magnumclient.v1.quotas.QuotasManager.delete')
    def test_quotas_delete_failure_no_resource(self, mock_delete):
        self._test_arg_failure('quotas-delete --project-id xxx',
                               self._mandatory_arg_error)
        mock_delete.assert_not_called()

    @mock.patch('magnumclient.v1.quotas.QuotasManager.get')
    def test_quotas_show_success(self, mock_show):
        self._test_arg_success('quotas-show --project-id abc '
                               '--resource Cluster')
        mock_show.assert_called_once_with('abc', 'Cluster')

    @mock.patch('magnumclient.v1.quotas.QuotasManager.get')
    def test_quotas_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('quotas-show',
                               self._mandatory_arg_error)
        mock_show.assert_not_called()

    @mock.patch('magnumclient.v1.quotas.QuotasManager.update')
    def test_quotas_update_success(self, mock_update):
        self._test_arg_success('quotas-update --project-id abc '
                               '--resource Cluster '
                               '--hard-limit 20')
        patch = {'project_id': 'abc', 'resource': 'Cluster', 'hard_limit': 20}
        mock_update.assert_called_once_with('abc', 'Cluster', patch)
