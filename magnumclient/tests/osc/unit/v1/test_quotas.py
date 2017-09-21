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

from magnumclient.osc.v1 import quotas as osc_quotas
from magnumclient.tests.osc.unit.v1 import fakes as magnum_fakes


class TestQuotas(magnum_fakes.TestMagnumClientOSCV1):

    def setUp(self):
        super(TestQuotas, self).setUp()

        self.quotas_mock = self.app.client_manager.container_infra.quotas


class TestQuotasCreate(TestQuotas):

    def setUp(self):
        super(TestQuotasCreate, self).setUp()
        attr = dict()
        attr['name'] = 'fake-quota'
        attr['project_id'] = 'abc'
        attr['resource'] = 'Cluster'
        self._quota = magnum_fakes.FakeQuota.create_one_quota(attr)

        self._default_args = {
            'project_id': 'abc',
            'resource': 'Cluster',
            'hard_limit': 1
        }

        self.quotas_mock.create = mock.Mock()
        self.quotas_mock.create.return_value = self._quota

        self.cmd = osc_quotas.CreateQuotas(self.app, None)

        self.data = tuple(map(lambda x: getattr(self._quota, x),
                              osc_quotas.QUOTA_ATTRIBUTES))

    def test_quotas_create(self):
        arglist = [
            '--project-id', 'abc',
            '--resource', 'Cluster'
        ]
        verifylist = [
            ('project_id', 'abc'),
            ('resource', 'Cluster')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.quotas_mock.create.assert_called_with(**self._default_args)

    def test_quotas_create_with_hardlimit(self):
        arglist = [
            '--project-id', 'abc',
            '--resource', 'Cluster',
            '--hard-limit', '10'
        ]
        verifylist = [
            ('project_id', 'abc'),
            ('resource', 'Cluster'),
            ('hard_limit', 10)
        ]
        self._default_args['hard_limit'] = 10
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.quotas_mock.create.assert_called_with(**self._default_args)

    def test_quotas_create_wrong_projectid(self):
        arglist = ['abcd']
        verifylist = [
            ('project_id', 'abcd')
        ]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_quotas_create_missing_args(self):
        arglist = []
        verifylist = []
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_quotas_create_with_wrong_args(self):
        arglist = [
            '--project-id', 'abc',
            '--resources', 'Cluster',  # Misspelling 'resources'
            '--hard-limit', '10'
        ]
        verifylist = []
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestQuotasDelete(TestQuotas):

    def setUp(self):
        super(TestQuotasDelete, self).setUp()

        self.quotas_mock.delete = mock.Mock()
        self.quotas_mock.delete.return_value = None

        self.cmd = osc_quotas.DeleteQuotas(self.app, None)

    def test_quotas_delete(self):
        arglist = [
            '--project-id', 'abc',
            '--resource', 'Cluster'
        ]
        verifylist = [
            ('project_id', 'abc'),
            ('resource', 'Cluster')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.quotas_mock.delete.assert_called_with('abc', 'Cluster')

    def test_quotas_delete_no_project_id(self):
        arglist = [
            '--resource', 'Cluster'
        ]
        verifylist = [
            ('resource', 'Cluster')
        ]
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_quotas_delete_no_resource(self):
        arglist = [
            '--project-id', 'abc',
        ]
        verifylist = [
            ('project_id', 'abc')
        ]
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_quotas_delete_missing_args(self):
        arglist = []
        verifylist = []
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_quotas_delete_wrong_args(self):
        arglist = [
            '--project-ids', 'abc',  # Misspelling 'ids' instead of 'id'
            '--resource', 'Cluster'
        ]
        verifylist = []
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestQuotasShow(TestQuotas):

    def setUp(self):
        super(TestQuotasShow, self).setUp()

        attr = dict()
        attr['name'] = 'fake-quota'
        attr['project_id'] = 'abc'
        attr['resource'] = 'Cluster'
        self._quota = magnum_fakes.FakeQuota.create_one_quota(attr)

        self._default_args = {
            'project_id': 'abc',
            'resource': 'Cluster',
        }

        self.quotas_mock.get = mock.Mock()
        self.quotas_mock.get.return_value = self._quota

        self.cmd = osc_quotas.ShowQuotas(self.app, None)

        self.data = tuple(map(lambda x: getattr(self._quota, x),
                              osc_quotas.QUOTA_ATTRIBUTES))

    def test_quotas_show(self):
        arglist = [
            '--project-id', 'abc',
            '--resource', 'Cluster'
        ]
        verifylist = [
            ('project_id', 'abc'),
            ('resource', 'Cluster')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.quotas_mock.get.assert_called_with('abc', 'Cluster')

    def test_quotas_show_missing_args(self):
        arglist = []
        verifylist = []
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestQuotasUpdate(TestQuotas):

    def setUp(self):
        super(TestQuotasUpdate, self).setUp()
        attr = dict()
        attr['name'] = 'fake-quota'
        attr['project_id'] = 'abc'
        attr['resource'] = 'Cluster'
        self._quota = magnum_fakes.FakeQuota.create_one_quota(attr)

        self._default_args = {
            'project_id': 'abc',
            'resource': 'Cluster',
            'hard_limit': 10
        }

        self.quotas_mock.update = mock.Mock()
        self.quotas_mock.update.return_value = self._quota

        self.cmd = osc_quotas.UpdateQuotas(self.app, None)

    def test_quotas_update(self):
        arglist = [
            '--project-id', 'abc',
            '--resource', 'Cluster',
            '--hard-limit', '10'
        ]
        verifylist = [
            ('project_id', 'abc'),
            ('resource', 'Cluster'),
            ('hard_limit', 10)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.quotas_mock.update.assert_called_with('abc', 'Cluster',
                                                   self._default_args)

    def test_quotas_update_missing_args(self):
        arglist = ['abcd']
        verifylist = [
            ('project_id', 'abcd')
        ]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_quotas_update_wrong_args(self):
        arglist = [
            '--project-id', 'abc',
            '--resource', 'Cluster',
            '--hard-limits', '10'  # Misspelling 'hard-limits'
        ]
        verifylist = [
            ('project_id', 'abc'),
            ('resource', 'Cluster'),
            ('hard_limit', 10)
        ]

        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)


class TestQuotasList(TestQuotas):

    def setUp(self):
        super(TestQuotasList, self).setUp()
        attr = dict()
        attr['name'] = 'fake-quota'
        attr['project_id'] = 'abc'
        attr['resource'] = 'Cluster'
        self._quota = magnum_fakes.FakeQuota.create_one_quota(attr)

        self.quotas_mock.list = mock.Mock()
        self.quotas_mock.list.return_value = [self._quota]

        self.cmd = osc_quotas.ListQuotas(self.app, None)

    def test_quotas_list_with_no_options(self):
        arglist = [
        ]
        verifylist = [
            ('limit', None),
            ('sort_key', None),
            ('sort_dir', None),
            ('marker', None),
            ('all_tenants', False)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.quotas_mock.list.assert_called_with(
            limit=None,
            sort_dir=None,
            sort_key=None,
            marker=None,
            all_tenants=False
        )

    def test_quotas_list_wrong_args(self):
        arglist = ['--wrong']
        verifylist = [
            ('wrong')
        ]
        self.assertRaises(magnum_fakes.MagnumParseException,
                          self.check_parser, self.cmd, arglist, verifylist)
