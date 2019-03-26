# Copyright (c) 2018 European Organization for Nuclear Research.
# All Rights Reserved.
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

from magnumclient.osc.v1 import nodegroups as osc_nodegroups
from magnumclient.tests.osc.unit.v1 import fakes as magnum_fakes


class TestNodeGroup(magnum_fakes.TestMagnumClientOSCV1):

    def setUp(self):
        super(TestNodeGroup, self).setUp()
        self.ng_mock = self.app.client_manager.container_infra.nodegroups


class TestNodeGroupShow(TestNodeGroup):

    def setUp(self):
        super(TestNodeGroupShow, self).setUp()

        self.nodegroup = magnum_fakes.FakeNodeGroup.create_one_nodegroup()
        self.ng_mock.get = mock.Mock()
        self.ng_mock.get.return_value = self.nodegroup

        self.data = tuple(map(lambda x: getattr(self.nodegroup, x),
                              osc_nodegroups.NODEGROUP_ATTRIBUTES))

        # Get the command object to test
        self.cmd = osc_nodegroups.ShowNodeGroup(self.app, None)

    def test_nodegroup_show_pass(self):
        arglist = ['fake-cluster', 'fake-nodegroup']
        verifylist = [
            ('cluster', 'fake-cluster'),
            ('nodegroup', 'fake-nodegroup')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.ng_mock.get.assert_called_with(
            'fake-cluster', 'fake-nodegroup')
        self.assertEqual(osc_nodegroups.NODEGROUP_ATTRIBUTES, columns)
        self.assertEqual(self.data, data)

    def test_nodegroup_show_no_nodegroup_fail(self):
        arglist = ['fake-cluster']
        verifylist = [
            ('cluster', 'fake-cluster'),
            ('nodegroup', '')
        ]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_nodegroup_show_no_args(self):
        arglist = []
        verifylist = [
            ('cluster', ''),
            ('nodegroup', '')
        ]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestNodeGroupList(TestNodeGroup):

    nodegroup = magnum_fakes.FakeNodeGroup.create_one_nodegroup()

    columns = ['uuid', 'name', 'flavor_id', 'node_count', 'role']

    datalist = (
        (
            nodegroup.uuid,
            nodegroup.name,
            nodegroup.flavor_id,
            nodegroup.node_count,
            nodegroup.role,
        ),
    )

    def setUp(self):
        super(TestNodeGroupList, self).setUp()
        self.ng_mock.list = mock.Mock()
        self.ng_mock.list.return_value = [self.nodegroup]

        # Get the command object to test
        self.cmd = osc_nodegroups.ListNodeGroup(self.app, None)

    def test_nodegroup_list_no_options(self):
        arglist = []
        verifylist = [
            ('cluster', ''),
            ('limit', None),
            ('sort_key', None),
            ('sort_dir', None),
        ]
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_nodegroup_list_ok(self):
        arglist = ['fake-cluster']
        verifylist = [
            ('cluster', 'fake-cluster'),
            ('limit', None),
            ('sort_key', None),
            ('sort_dir', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.ng_mock.list.assert_called_with(
            'fake-cluster',
            limit=None,
            sort_dir=None,
            sort_key=None,
            role=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_nodegroup_list_options(self):
        arglist = [
            'fake-cluster',
            '--limit', '1',
            '--sort-key', 'key',
            '--sort-dir', 'asc'
        ]
        verifylist = [
            ('cluster', 'fake-cluster'),
            ('limit', 1),
            ('sort_key', 'key'),
            ('sort_dir', 'asc')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.ng_mock.list.assert_called_with(
            'fake-cluster',
            limit=1,
            sort_dir='asc',
            sort_key='key',
            role=None
        )
