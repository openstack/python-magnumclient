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

import copy
import mock
from mock import call

from magnumclient.osc.v1 import nodegroups as osc_nodegroups
from magnumclient.tests.osc.unit.v1 import fakes as magnum_fakes


class TestNodeGroup(magnum_fakes.TestMagnumClientOSCV1):

    def setUp(self):
        super(TestNodeGroup, self).setUp()
        self.ng_mock = self.app.client_manager.container_infra.nodegroups


class TestNodeGroupCreate(TestNodeGroup):

    def setUp(self):
        super(TestNodeGroupCreate, self).setUp()
        self.nodegroup = magnum_fakes.FakeNodeGroup.create_one_nodegroup()

        self.ng_mock.create = mock.Mock()
        self.ng_mock.create.return_value = self.nodegroup

        self.ng_mock.get = mock.Mock()
        self.ng_mock.get.return_value = copy.deepcopy(self.nodegroup)

        self.ng_mock.update = mock.Mock()
        self.ng_mock.update.return_value = self.nodegroup

        self._default_args = {
            'name': 'fake-nodegroup',
            'node_count': 1,
            'role': 'worker',
            'min_node_count': 1,
            'max_node_count': None,
        }

        # Get the command object to test
        self.cmd = osc_nodegroups.CreateNodeGroup(self.app, None)

        self.data = tuple(map(lambda x: getattr(self.nodegroup, x),
                              osc_nodegroups.NODEGROUP_ATTRIBUTES))

    def test_nodegroup_create_required_args_pass(self):
        """Verifies required arguments."""

        arglist = [
            self.nodegroup.cluster_id,
            self.nodegroup.name
        ]
        verifylist = [
            ('cluster', self.nodegroup.cluster_id),
            ('name', self.nodegroup.name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.ng_mock.create.assert_called_with(self.nodegroup.cluster_id,
                                               **self._default_args)

    def test_nodegroup_create_missing_required_arg(self):
        """Verifies missing required arguments."""

        arglist = [
            self.nodegroup.name
        ]
        verifylist = [
            ('name', self.nodegroup.name)
        ]
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_nodegroup_create_with_labels(self):
        """Verifies labels are properly parsed when given as argument."""

        expected_args = self._default_args
        expected_args['labels'] = {
            'arg1': 'value1', 'arg2': 'value2'
        }

        arglist = [
            '--labels', 'arg1=value1',
            '--labels', 'arg2=value2',
            self.nodegroup.cluster_id,
            self.nodegroup.name
        ]
        verifylist = [
            ('labels', ['arg1=value1', 'arg2=value2']),
            ('name', self.nodegroup.name),
            ('cluster', self.nodegroup.cluster_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.ng_mock.create.assert_called_with(self.nodegroup.cluster_id,
                                               **expected_args)


class TestNodeGroupDelete(TestNodeGroup):

    def setUp(self):
        super(TestNodeGroupDelete, self).setUp()

        self.ng_mock.delete = mock.Mock()
        self.ng_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = osc_nodegroups.DeleteNodeGroup(self.app, None)

    def test_nodegroup_delete_one(self):
        arglist = ['foo', 'fake-nodegroup']
        verifylist = [
            ('cluster', 'foo'),
            ('nodegroup', ['fake-nodegroup'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.ng_mock.delete.assert_called_with('foo', 'fake-nodegroup')

    def test_nodegroup_delete_multiple(self):
        arglist = ['foo', 'fake-nodegroup1', 'fake-nodegroup2']
        verifylist = [
            ('cluster', 'foo'),
            ('nodegroup', ['fake-nodegroup1', 'fake-nodegroup2'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.ng_mock.delete.assert_has_calls(
            [call('foo', 'fake-nodegroup1'), call('foo', 'fake-nodegroup2')]
        )

    def test_nodegroup_delete_no_args(self):
        arglist = []
        verifylist = [
            ('cluster', ''),
            ('nodegroup', [])
        ]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestNodeGroupUpdate(TestNodeGroup):

    def setUp(self):
        super(TestNodeGroupUpdate, self).setUp()

        self.ng_mock.update = mock.Mock()
        self.ng_mock.update.return_value = None

        # Get the command object to test
        self.cmd = osc_nodegroups.UpdateNodeGroup(self.app, None)

    def test_nodegroup_update_pass(self):
        arglist = ['foo', 'ng1', 'remove', 'bar']
        verifylist = [
            ('cluster', 'foo'),
            ('nodegroup', 'ng1'),
            ('op', 'remove'),
            ('attributes', [['bar']])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.ng_mock.update.assert_called_with(
            'foo', 'ng1',
            [{'op': 'remove', 'path': '/bar'}]
        )

    def test_nodegroup_update_bad_op(self):
        arglist = ['cluster', 'ng1', 'foo', 'bar']
        verifylist = [
            ('cluster', 'cluster'),
            ('nodegroup', 'ng1'),
            ('op', 'foo'),
            ('attributes', ['bar'])
        ]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


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

    columns = ['uuid', 'name', 'flavor_id', 'image_id', 'node_count',
               'status', 'role']

    datalist = (
        (
            nodegroup.uuid,
            nodegroup.name,
            nodegroup.flavor_id,
            nodegroup.image_id,
            nodegroup.node_count,
            nodegroup.status,
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
