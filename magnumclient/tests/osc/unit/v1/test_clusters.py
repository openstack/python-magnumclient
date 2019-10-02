#   Copyright 2016 Easystack. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import copy
import mock
import os
import sys
import tempfile

from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from mock import call

from magnumclient import exceptions
from magnumclient.osc.v1 import clusters as osc_clusters
from magnumclient.tests.osc.unit.v1 import fakes as magnum_fakes


class TestCluster(magnum_fakes.TestMagnumClientOSCV1):

    def setUp(self):
        super(TestCluster, self).setUp()

        self.clusters_mock = self.app.client_manager.container_infra.clusters
        self.certificates_mock = \
            self.app.client_manager.container_infra.certificates


class TestClusterCreate(TestCluster):

    def setUp(self):
        super(TestClusterCreate, self).setUp()

        attr = dict()
        attr['name'] = 'fake-cluster-1'
        self._cluster = magnum_fakes.FakeCluster.create_one_cluster(attr)

        self._default_args = {
            'cluster_template_id': 'fake-ct',
            'create_timeout': 60,
            'discovery_url': None,
            'keypair': None,
            'master_count': 1,
            'name': 'fake-cluster-1',
            'node_count': 1,
        }

        self.clusters_mock.create = mock.Mock()
        self.clusters_mock.create.return_value = self._cluster

        self.clusters_mock.get = mock.Mock()
        self.clusters_mock.get.return_value = copy.deepcopy(self._cluster)

        self.clusters_mock.update = mock.Mock()
        self.clusters_mock.update.return_value = self._cluster

        # Get the command object to test
        self.cmd = osc_clusters.CreateCluster(self.app, None)

        self.data = tuple(map(lambda x: getattr(self._cluster, x),
                              osc_clusters.CLUSTER_ATTRIBUTES))

    def test_cluster_create_required_args_pass(self):
        """Verifies required arguments."""

        arglist = [
            '--cluster-template', self._cluster.cluster_template_id,
            self._cluster.name
        ]
        verifylist = [
            ('cluster_template', self._cluster.cluster_template_id),
            ('name', self._cluster.name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.clusters_mock.create.assert_called_with(**self._default_args)

    def test_cluster_create_missing_required_arg(self):
        """Verifies missing required arguments."""

        arglist = [
            self._cluster.name
        ]
        verifylist = [
            ('name', self._cluster.name)
        ]
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_cluster_create_with_labels(self):
        """Verifies labels are properly parsed when given as argument."""

        expected_args = self._default_args
        expected_args['labels'] = {
            'arg1': 'value1', 'arg2': 'value2'
        }

        arglist = [
            '--cluster-template', self._cluster.cluster_template_id,
            '--labels', 'arg1=value1',
            '--labels', 'arg2=value2',
            self._cluster.name
        ]
        verifylist = [
            ('cluster_template', self._cluster.cluster_template_id),
            ('labels', ['arg1=value1', 'arg2=value2']),
            ('name', self._cluster.name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.clusters_mock.create.assert_called_with(**expected_args)


class TestClusterDelete(TestCluster):

    def setUp(self):
        super(TestClusterDelete, self).setUp()

        self.clusters_mock.delete = mock.Mock()
        self.clusters_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = osc_clusters.DeleteCluster(self.app, None)

    def test_cluster_delete_one(self):
        arglist = ['foo']
        verifylist = [('cluster', ['foo'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.delete.assert_called_with('foo')

    def test_cluster_delete_multiple(self):
        arglist = ['foo', 'bar']
        verifylist = [('cluster', ['foo', 'bar'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.delete.assert_has_calls([call('foo'), call('bar')])

    def test_cluster_delete_bad_uuid(self):
        arglist = ['foo']
        verifylist = [('cluster', ['foo'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        returns = self.cmd.take_action(parsed_args)

        self.assertEqual(returns, None)

    def test_cluster_delete_no_uuid(self):
        arglist = []
        verifylist = [('cluster', [])]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestClusterList(TestCluster):
    attr = dict()
    attr['name'] = 'fake-cluster-1'
    _cluster = magnum_fakes.FakeCluster.create_one_cluster(attr)

    columns = [
        'uuid',
        'name',
        'keypair',
        'node_count',
        'master_count',
        'status',
        'health_status'
    ]

    datalist = (
        (
            _cluster.uuid,
            _cluster.name,
            _cluster.keypair,
            _cluster.node_count,
            _cluster.master_count,
            _cluster.status,
            _cluster.health_status,
        ),
    )

    def setUp(self):
        super(TestClusterList, self).setUp()

        self.clusters_mock.list = mock.Mock()
        self.clusters_mock.list.return_value = [self._cluster]

        # Get the command object to test
        self.cmd = osc_clusters.ListCluster(self.app, None)

    def test_cluster_list_no_options(self):
        arglist = []
        verifylist = [
            ('limit', None),
            ('sort_key', None),
            ('sort_dir', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.clusters_mock.list.assert_called_with(
            limit=None,
            sort_dir=None,
            sort_key=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_cluster_list_options(self):
        arglist = [
            '--limit', '1',
            '--sort-key', 'key',
            '--sort-dir', 'asc'
        ]
        verifylist = [
            ('limit', 1),
            ('sort_key', 'key'),
            ('sort_dir', 'asc')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.list.assert_called_with(
            limit=1,
            sort_dir='asc',
            sort_key='key',
        )

    def test_cluster_list_bad_sort_dir_fail(self):
        arglist = [
            '--sort-dir', 'foo'
        ]
        verifylist = [
            ('limit', None),
            ('sort_key', None),
            ('sort_dir', 'foo'),
            ('fields', None),
        ]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestClusterUpdate(TestCluster):

    def setUp(self):
        super(TestClusterUpdate, self).setUp()

        self.clusters_mock.update = mock.Mock()
        self.clusters_mock.update.return_value = None

        # Get the command object to test
        self.cmd = osc_clusters.UpdateCluster(self.app, None)

    def test_cluster_update_pass(self):
        arglist = ['foo', 'remove', 'bar']
        verifylist = [
            ('cluster', 'foo'),
            ('op', 'remove'),
            ('attributes', [['bar']]),
            ('rollback', False)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.update.assert_called_with(
            'foo',
            [{'op': 'remove', 'path': '/bar'}]
        )

    def test_cluster_update_bad_op(self):
        arglist = ['foo', 'bar', 'snafu']
        verifylist = [
            ('cluster', 'foo'),
            ('op', 'bar'),
            ('attributes', ['snafu']),
            ('rollback', False)
        ]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestClusterShow(TestCluster):

    def setUp(self):
        super(TestClusterShow, self).setUp()

        attr = dict()
        attr['name'] = 'fake-cluster-1'
        self._cluster = magnum_fakes.FakeCluster.create_one_cluster(attr)

        self.clusters_mock.get = mock.Mock()
        self.clusters_mock.get.return_value = self._cluster

        # Get the command object to test
        self.cmd = osc_clusters.ShowCluster(self.app, None)

        self.data = tuple(map(lambda x: getattr(self._cluster, x),
                              osc_clusters.CLUSTER_ATTRIBUTES))

    def test_cluster_show_pass(self):
        arglist = ['fake-cluster']
        verifylist = [
            ('cluster', 'fake-cluster')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.clusters_mock.get.assert_called_with('fake-cluster')
        self.assertEqual(osc_clusters.CLUSTER_ATTRIBUTES, columns)
        self.assertEqual(self.data, data)

    def test_cluster_show_no_cluster_fail(self):
        arglist = []
        verifylist = []

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


@contextmanager
def capture(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, StringIO()
    try:
        command(*args, **kwargs)
        sys.stdout.seek(0)
        yield sys.stdout.read()
    finally:
        sys.stdout = out


class TestClusterConfig(TestCluster):

    def setUp(self):
        super(TestClusterConfig, self).setUp()

        attr = dict()
        attr['name'] = 'fake-cluster-1'
        attr['status'] = 'CREATE_COMPLETE'
        self._cluster = magnum_fakes.FakeCluster.create_one_cluster(attr)

        self.clusters_mock.get = mock.Mock()
        self.clusters_mock.get.return_value = self._cluster

        cert = magnum_fakes.FakeCert(pem='foo bar')
        self.certificates_mock.create = mock.Mock()
        self.certificates_mock.create.return_value = cert
        self.certificates_mock.get = mock.Mock()
        self.certificates_mock.get.return_value = cert

        # Fake the cluster_template
        attr = dict()
        attr['name'] = 'fake-ct'
        self._cluster_template = \
            magnum_fakes.FakeClusterTemplate.create_one_cluster_template(attr)

        self.cluster_templates_mock = \
            self.app.client_manager.container_infra.cluster_templates
        self.cluster_templates_mock.get = mock.Mock()
        self.cluster_templates_mock.get.return_value = self._cluster_template

        # Get the command object to test
        self.cmd = osc_clusters.ConfigCluster(self.app, None)

    def test_cluster_config_no_cluster_fail(self):
        arglist = []
        verifylist = []

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    @mock.patch.dict(os.environ, {'SHELL': '/bin/bash'})
    def test_cluster_config_custom_dir_with_config_only_works_if_force(self):
        tmp_dir = tempfile.mkdtemp()
        open(os.path.join(tmp_dir, 'config'), 'a').close()  # touch config

        arglist = ['fake-cluster', '--dir', tmp_dir]
        verifylist = [
            ('cluster', 'fake-cluster'),
            ('force', False),
            ('dir', tmp_dir),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action, parsed_args)

        self.clusters_mock.get.assert_called_with('fake-cluster')

        arglist = ['fake-cluster', '--force', '--dir', tmp_dir]
        verifylist = [
            ('cluster', 'fake-cluster'),
            ('force', True),
            ('dir', tmp_dir),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        expected_value = '''\
export KUBECONFIG={}/config

'''.format(tmp_dir)

        with capture(self.cmd.take_action, parsed_args) as output:
            self.assertEqual(expected_value, output)

        self.clusters_mock.get.assert_called_with('fake-cluster')

    @mock.patch.dict(os.environ, {'SHELL': '/bin/bash'})
    def test_cluster_config_with_custom_dir(self):
        tmp_dir = tempfile.mkdtemp()

        arglist = ['fake-cluster', '--dir', tmp_dir]
        verifylist = [
            ('cluster', 'fake-cluster'),
            ('dir', tmp_dir),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_value = '''\
export KUBECONFIG={}/config

'''.format(tmp_dir)

        with capture(self.cmd.take_action, parsed_args) as output:
            self.assertEqual(expected_value, output)

        self.clusters_mock.get.assert_called_with('fake-cluster')

    @mock.patch.dict(os.environ, {'SHELL': '/bin/bash'})
    def test_cluster_config_creates_config_in_cwd_if_not_dir_specified(self):
        tmp_dir = tempfile.mkdtemp()
        os.chdir(tmp_dir)

        arglist = ['fake-cluster']
        verifylist = [
            ('cluster', 'fake-cluster'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        expected_value = '''\
export KUBECONFIG={}/config

'''.format(os.getcwd())

        with capture(self.cmd.take_action, parsed_args) as output:
            self.assertEqual(expected_value, output)

        self.clusters_mock.get.assert_called_with('fake-cluster')


class TestClusterResize(TestCluster):

    def setUp(self):
        super(TestClusterResize, self).setUp()
        self.cluster = mock.Mock()
        self.cluster.uuid = "UUID1"
        self.clusters_mock.resize = mock.Mock()
        self.clusters_mock.resize.return_value = None

        self.clusters_mock.get = mock.Mock()
        self.clusters_mock.get.return_value = self.cluster

        # Get the command object to test
        self.cmd = osc_clusters.ResizeCluster(self.app, None)

    def test_cluster_resize_pass(self):
        arglist = ['foo', '2']
        verifylist = [
            ('cluster', 'foo'),
            ('node_count', 2),
            ('nodes_to_remove', None),
            ('nodegroup', None)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.resize.assert_called_with(
            "UUID1", 2, None, None
        )


class TestClusterUpgrade(TestCluster):

    def setUp(self):
        super(TestClusterUpgrade, self).setUp()
        self.cluster = mock.Mock()
        self.cluster.uuid = "UUID1"
        self.clusters_mock.upgrade = mock.Mock()
        self.clusters_mock.upgrade.return_value = None

        self.clusters_mock.get = mock.Mock()
        self.clusters_mock.get.return_value = self.cluster

        # Get the command object to test
        self.cmd = osc_clusters.UpgradeCluster(self.app, None)

    def test_cluster_upgrade_pass(self):
        cluster_template_id = 'TEMPLATE_ID'
        arglist = ['foo', cluster_template_id]
        verifylist = [
            ('cluster', 'foo'),
            ('cluster_template', cluster_template_id),
            ('max_batch_size', 1),
            ('nodegroup', None)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.clusters_mock.upgrade.assert_called_with(
            "UUID1", cluster_template_id, 1, None
        )
