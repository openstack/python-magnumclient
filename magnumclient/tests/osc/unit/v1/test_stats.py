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

from magnumclient.osc.v1 import stats as osc_stats
from magnumclient.tests.osc.unit.v1 import fakes as magnum_fakes


class TestStats(magnum_fakes.TestMagnumClientOSCV1):

    def setUp(self):
        super(TestStats, self).setUp()

        self.clusters_mock = self.app.client_manager.container_infra.stats


class TestStatsList(TestStats):

    def setUp(self):
        super(TestStatsList, self).setUp()

        attr = dict()
        attr['name'] = 'fake-cluster-1'
        attr['project_id'] = 'abc'
        attr['node_count'] = 2
        attr['master_count'] = 1
        self._cluster = magnum_fakes.FakeCluster.create_one_cluster(attr)

        self.clusters_mock.list = mock.Mock()
        self.clusters_mock.list.return_value = self._cluster

        self.cmd = osc_stats.ListStats(self.app, None)

    def test_stats_list(self):
        arglist = ['abc']
        verifylist = [
            ('project_id', 'abc')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.list.assert_called_once_with(project_id='abc')

    def test_stats_list_wrong_projectid(self):
        arglist = ['abcd']
        verifylist = [
            ('project_id', 'abcd')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.list.assert_called_once_with(project_id='abcd')

    def test_stats_list_missing_args(self):
        arglist = []
        verifylist = []
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)
