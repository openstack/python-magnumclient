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
from magnumclient.v1.stats import Stats


class FakeStats(Stats):
    def __init__(self, manager=None, info={}, **kwargs):
        Stats.__init__(self, manager=manager, info=info)
        self.clusters = kwargs.get('clusters', 0)
        self.nodes = kwargs.get('nodes', 0)


class ShellTest(shell_test_base.TestCommandLineArgument):

    def _get_expected_args_list(self, project_id=None):
        expected_args = {}
        expected_args['project_id'] = project_id
        return expected_args

    @mock.patch(
        'magnumclient.v1.stats.StatsManager.list')
    def test_stats_get_success(self, mock_list):
        self._test_arg_success('stats-list')
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.stats.StatsManager.list')
    def test_stats_get_success_with_arg(self, mock_list):
        self._test_arg_success('stats-list '
                               '--project-id 111 ')
        expected_args = self._get_expected_args_list('111')
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.stats.StatsManager.list')
    def test_stats_get_failure(self, mock_list):
        self._test_arg_failure('stats-list --wrong',
                               self._unrecognized_arg_error)
        mock_list.assert_not_called()
