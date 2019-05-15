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
from mock import call

from magnumclient.exceptions import InvalidAttribute
from magnumclient.osc.v1 import cluster_templates as osc_ct
from magnumclient.tests.osc.unit.v1 import fakes as magnum_fakes

from osc_lib import exceptions as osc_exceptions


class TestClusterTemplate(magnum_fakes.TestMagnumClientOSCV1):
    default_create_args = {
        'coe': 'kubernetes',
        'dns_nameserver': '8.8.8.8',
        'docker_storage_driver': 'devicemapper',
        'docker_volume_size': None,
        'external_network_id': 'public',
        'fixed_network': None,
        'fixed_subnet': None,
        'flavor_id': 'm1.medium',
        'http_proxy': None,
        'https_proxy': None,
        'image_id': 'fedora-atomic-latest',
        'keypair_id': None,
        'labels': {},
        'master_flavor_id': None,
        'master_lb_enabled': False,
        'name': 'fake-ct-1',
        'network_driver': None,
        'no_proxy': None,
        'public': False,
        'registry_enabled': False,
        'server_type': 'vm',
        'tls_disabled': False,
        'volume_driver': None,
    }

    def setUp(self):
        super(TestClusterTemplate, self).setUp()

        self.cluster_templates_mock = (
            self.app.client_manager.container_infra.cluster_templates)


class TestClusterTemplateCreate(TestClusterTemplate):

    def setUp(self):
        super(TestClusterTemplateCreate, self).setUp()

        attr = dict()
        attr['name'] = 'fake-ct-1'
        self.new_ct = (
            magnum_fakes.FakeClusterTemplate.create_one_cluster_template(attr))

        self.cluster_templates_mock.create = mock.Mock()
        self.cluster_templates_mock.create.return_value = self.new_ct

        self.cluster_templates_mock.get = mock.Mock()
        self.cluster_templates_mock.get.return_value = copy.deepcopy(
            self.new_ct)

        self.cluster_templates_mock.update = mock.Mock()
        self.cluster_templates_mock.update.return_value = self.new_ct

        # Get the command object to test
        self.cmd = osc_ct.CreateClusterTemplate(self.app, None)

        self.data = tuple(map(lambda x: getattr(self.new_ct, x),
                              osc_ct.CLUSTER_TEMPLATE_ATTRIBUTES))

    def test_cluster_template_create_required_args_pass(self):
        """Verifies required arguments."""

        arglist = [
            '--coe', self.new_ct.coe,
            '--external-network', self.new_ct.external_network_id,
            '--image', self.new_ct.image_id,
            self.new_ct.name
        ]
        verifylist = [
            ('coe', self.new_ct.coe),
            ('external_network', self.new_ct.external_network_id),
            ('image', self.new_ct.image_id),
            ('name', self.new_ct.name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.cluster_templates_mock.create.assert_called_with(
            **self.default_create_args)

    def test_cluster_template_create_missing_required_arg(self):
        """Verifies missing required arguments."""

        arglist = [
            '--external-network', self.new_ct.external_network_id,
            '--image', self.new_ct.image_id
        ]
        verifylist = [
            ('external_network', self.new_ct.external_network_id),
            ('image', self.new_ct.image_id)
        ]
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)
        # Verify all required args are checked and not just coe
        arglist.append('--coe')
        arglist.append(self.new_ct.coe)
        verifylist.append(('coe', self.new_ct.coe))
        arglist.remove('--image')
        arglist.remove(self.new_ct.image_id)
        verifylist.remove(('image', self.new_ct.image_id))
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

        arglist.remove('--external-network')
        arglist.remove(self.new_ct.external_network_id)
        verifylist.remove(
            ('external_network', self.new_ct.external_network_id))
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_cluster_template_create_floating_ips(self):
        """Verifies floating ip parameters."""
        arglist = [
            '--coe', self.new_ct.coe,
            '--external-network', self.new_ct.external_network_id,
            '--image', self.new_ct.image_id,
            '--floating-ip-enabled',
            self.new_ct.name
        ]
        verifylist = [
            ('coe', self.new_ct.coe),
            ('external_network', self.new_ct.external_network_id),
            ('image', self.new_ct.image_id),
            ('floating_ip_enabled', [True]),
            ('name', self.new_ct.name)
        ]
        self.default_create_args['floating_ip_enabled'] = True
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.default_create_args.pop('floating_ip_enabled')

        arglist.append('--floating-ip-disabled')
        verifylist.remove(('floating_ip_enabled', [True]))
        verifylist.append(('floating_ip_enabled', [True, False]))
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(InvalidAttribute, self.cmd.take_action, parsed_args)


class TestClusterTemplateDelete(TestClusterTemplate):

    def setUp(self):
        super(TestClusterTemplateDelete, self).setUp()

        self.cluster_templates_mock.delete = mock.Mock()
        self.cluster_templates_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = osc_ct.DeleteClusterTemplate(self.app, None)

    def test_cluster_template_delete_one(self):
        arglist = ['foo']
        verifylist = [('cluster-templates', ['foo'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.cluster_templates_mock.delete.assert_called_with('foo')

    def test_cluster_template_delete_multiple(self):
        arglist = ['foo', 'bar']
        verifylist = [('cluster-templates', ['foo', 'bar'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.cluster_templates_mock.delete.assert_has_calls([call('foo'),
                                                            call('bar')])

    def test_cluster_template_delete_bad_uuid(self):
        self.cluster_templates_mock.delete.side_effect = (
            osc_exceptions.NotFound(404))
        arglist = ['foo']
        verifylist = [('cluster-templates', ['foo'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        returns = self.cmd.take_action(parsed_args)

        self.assertEqual(returns, None)

    def test_cluster_template_delete_no_uuid(self):
        arglist = []
        verifylist = [('cluster-templates', [])]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestClusterTemplateList(TestClusterTemplate):
    attr = dict()
    attr['name'] = 'fake-ct-1'

    _cluster_template = (
        magnum_fakes.FakeClusterTemplate.create_one_cluster_template(attr))

    attr['name'] = 'fake-ct-2'

    _cluster_template2 = (
        magnum_fakes.FakeClusterTemplate.create_one_cluster_template(attr))

    columns = [
        'uuid',
        'name'
    ]

    datalist = (
        (_cluster_template.uuid, _cluster_template.name),
        (_cluster_template2.uuid, _cluster_template2.name)
    )

    def setUp(self):
        super(TestClusterTemplateList, self).setUp()

        self.cluster_templates_mock.list = mock.Mock()
        self.cluster_templates_mock.list.return_value = [
            self._cluster_template, self._cluster_template2
        ]

        # Get the command object to test
        self.cmd = osc_ct.ListTemplateCluster(self.app, None)

    def test_cluster_template_list_no_options(self):
        arglist = []
        verifylist = [
            ('limit', None),
            ('sort_key', None),
            ('sort_dir', None),
            ('fields', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.cluster_templates_mock.list.assert_called_with(
            limit=None,
            sort_dir=None,
            sort_key=None,
        )
        self.assertEqual(self.columns, columns)
        index = 0
        for d in data:
            self.assertEqual(self.datalist[index], d)
            index += 1

    def test_cluster_template_list_options(self):
        arglist = [
            '--limit', '1',
            '--sort-key', 'key',
            '--sort-dir', 'asc',
            '--fields', 'fields'
        ]
        verifylist = [
            ('limit', 1),
            ('sort_key', 'key'),
            ('sort_dir', 'asc'),
            ('fields', 'fields'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.cluster_templates_mock.list.assert_called_with(
            limit=1,
            sort_dir='asc',
            sort_key='key',
        )

    def test_cluster_template_list_bad_sort_dir_fail(self):
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


class TestClusterTemplateShow(TestClusterTemplate):
    attr = dict()
    attr['name'] = 'fake-ct-1'

    _cluster_template = (
        magnum_fakes.FakeClusterTemplate.create_one_cluster_template(attr))

    columns = osc_ct.CLUSTER_TEMPLATE_ATTRIBUTES

    def setUp(self):
        super(TestClusterTemplateShow, self).setUp()

        datalist = map(lambda x: getattr(self._cluster_template, x),
                       self.columns)

        self.show_data_list = tuple(map(lambda x: x if x is not None else '-',
                                        datalist))

        self.cluster_templates_mock.get = mock.Mock()
        self.cluster_templates_mock.get.return_value = self._cluster_template

        # Get the command object to test
        self.cmd = osc_ct.ShowClusterTemplate(self.app, None)

    def test_cluster_template_show(self):
        arglist = ['fake-ct-1']
        verifylist = [('cluster-template', 'fake-ct-1')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.cluster_templates_mock.get.assert_called_with('fake-ct-1')
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.show_data_list, data)

    def test_cluster_template_show_no_ct_fail(self):
        arglist = []
        verifylist = []

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestClusterTemplateUpdate(TestClusterTemplate):

    def setUp(self):
        super(TestClusterTemplateUpdate, self).setUp()

        attr = dict()
        attr['name'] = 'fake-ct-1'
        ct = magnum_fakes.FakeClusterTemplate.create_one_cluster_template(attr)

        self.cluster_templates_mock.update = mock.Mock()
        self.cluster_templates_mock.update.return_value = ct

        # Get the command object to test
        self.cmd = osc_ct.UpdateClusterTemplate(self.app, None)

    def test_cluster_template_update_pass(self):
        arglist = ['foo', 'remove', 'bar']
        verifylist = [
            ('cluster-template', 'foo'),
            ('op', 'remove'),
            ('attributes', [['bar']])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.cluster_templates_mock.update.assert_called_with(
            'foo',
            [{'op': 'remove', 'path': '/bar'}]
        )

    def test_cluster_template_update_bad_op(self):
        arglist = ['foo', 'bar', 'snafu']
        verifylist = [
            ('cluster-template', 'foo'),
            ('op', 'bar'),
            ('attributes', ['snafu'])
        ]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)
