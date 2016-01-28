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

import re
import sys

import fixtures
from keystoneauth1 import fixture
import mock
import six
from testtools import matchers

from magnumclient import exceptions
import magnumclient.shell
from magnumclient.tests import utils

FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where/v2.0'}

FAKE_ENV2 = {'OS_USER_ID': 'user_id',
             'OS_PASSWORD': 'password',
             'OS_TENANT_ID': 'tenant_id',
             'OS_AUTH_URL': 'http://no.where/v2.0'}

FAKE_ENV3 = {'OS_USERNAME': 'username',
             'OS_PASSWORD': 'password',
             'OS_TENANT_ID': 'tenant_id',
             'OS_AUTH_URL': 'http://no.where/v2.0'}

FAKE_ENV4 = {'OS_USERNAME': 'username',
             'OS_PASSWORD': 'password',
             'OS_TENANT_ID': 'tenant_id',
             'OS_USER_DOMAIN_NAME': 'Default',
             'OS_PROJECT_DOMAIN_NAME': 'Default',
             'OS_AUTH_URL': 'http://no.where/v3'}


def _create_ver_list(versions):
    return {'versions': {'values': versions}}


class ParserTest(utils.TestCase):

    def setUp(self):
        super(ParserTest, self).setUp()
        self.parser = magnumclient.shell.MagnumClientArgumentParser()

    def test_ambiguous_option(self):
        self.parser.add_argument('--tic')
        self.parser.add_argument('--tac')
        try:
            self.parser.parse_args(['--t'])
        except SystemExit as err:
            self.assertEqual(2, err.code)
        else:
            self.fail('SystemExit not raised')


class ShellTest(utils.TestCase):
    AUTH_URL = utils.FAKE_ENV['OS_AUTH_URL']

    _msg_no_tenant_project = ("You must provide a tenant name or tenant id"
                              " via --os-tenant-name, --os-tenant-id,"
                              " env[OS_TENANT_NAME] or env[OS_TENANT_ID]")

    def setUp(self):
        super(ShellTest, self).setUp()
        self.nc_util = mock.patch(
            'magnumclient.openstack.common.cliutils.isunauthenticated').start()
        self.nc_util.return_value = False

    def test_help_unknown_command(self):
        self.assertRaises(exceptions.CommandError, self.shell, 'help foofoo')

    def test_help(self):
        required = [
            '.*?^usage: ',
            '.*?^\s+container-stop\s+Stop specified container.',
            '.*?^See "magnum help COMMAND" for help on a specific command',
        ]
        stdout, stderr = self.shell('help')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_help_on_subcommand(self):
        required = [
            '.*?^usage: magnum bay-create',
            '.*?^Create a bay.',
            '.*?^Optional arguments:',
        ]
        stdout, stderr = self.shell('help bay-create')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_help_no_options(self):
        required = [
            '.*?^usage: ',
            '.*?^\s+container-stop\s+Stop specified container.',
            '.*?^See "magnum help COMMAND" for help on a specific command',
        ]
        stdout, stderr = self.shell('')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_bash_completion(self):
        stdout, stderr = self.shell('bash-completion')
        # just check we have some output
        required = [
            '.*--type',
            '.*--json',
            '.*help',
            '.*bay-show',
            '.*--bay']
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_no_username(self):
        required = ('You must provide a username via either'
                    ' --os-username or env[OS_USERNAME]')
        self.make_env(exclude='OS_USERNAME')
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    def test_no_user_id(self):
        required = ('You must provide a username via'
                    ' either --os-username or env[OS_USERNAME]')
        self.make_env(exclude='OS_USER_ID', fake_env=FAKE_ENV2)
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    def test_no_tenant_name(self):
        required = self._msg_no_tenant_project
        self.make_env(exclude='OS_TENANT_NAME')
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    def test_no_tenant_id(self):
        required = self._msg_no_tenant_project
        self.make_env(exclude='OS_TENANT_ID', fake_env=FAKE_ENV3)
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    def test_no_auth_url(self):
        required = ('You must provide an auth url'
                    ' via either --os-auth-url or env[OS_AUTH_URL] or'
                    ' specify an auth_system which defines a default url'
                    ' with --os-auth-system or env[OS_AUTH_SYSTEM]',)
        self.make_env(exclude='OS_AUTH_URL')
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

    # FIXME(madhuri) Remove this harcoded v1 Client class.
    #                In future, when a new version of API will
    #                introduce, this needs to be dynamic then.
    @mock.patch('magnumclient.v1.client.Client')
    def test_service_type(self, mock_client):
        self.make_env()
        self.shell('bay-list')
        _, client_kwargs = mock_client.call_args_list[0]
        self.assertEqual('container', client_kwargs['service_type'])

    @mock.patch('magnumclient.v1.bays_shell.do_bay_list')
    @mock.patch('magnumclient.v1.client.ksa_session')
    def test_insecure(self, mock_session, mock_bay_list):
        self.make_env()
        self.shell('--insecure bay-list')
        _, session_kwargs = mock_session.Session.call_args_list[0]
        self.assertEqual(False, session_kwargs['verify'])

    @mock.patch('sys.stdin', side_effect=mock.MagicMock)
    @mock.patch('getpass.getpass', side_effect=EOFError)
    def test_no_password(self, mock_getpass, mock_stdin):
        required = ('Expecting a password provided'
                    ' via either --os-password, env[OS_PASSWORD],'
                    ' or prompted response',)
        self.make_env(exclude='OS_PASSWORD')
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

    @mock.patch('sys.argv', ['magnum'])
    @mock.patch('sys.stdout', six.StringIO())
    @mock.patch('sys.stderr', six.StringIO())
    def test_main_noargs(self):
        # Ensure that main works with no command-line arguments
        try:
            magnumclient.shell.main()
        except SystemExit:
            self.fail('Unexpected SystemExit')

        # We expect the normal usage as a result
        self.assertIn('Command-line interface to the OpenStack Magnum API',
                      sys.stdout.getvalue())

    @mock.patch('magnumclient.v1.client.Client')
    def _test_main_region(self, command, expected_region_name, mock_client):
        self.shell(command)
        mock_client.assert_called_once_with(
            username='username', api_key='password',
            endpoint_type='publicURL', project_id='',
            project_name='tenant_name', auth_url=self.AUTH_URL,
            service_type='container', region_name=expected_region_name,
            project_domain_id='', project_domain_name='',
            user_domain_id='', user_domain_name='',
            magnum_url=None, insecure=False)

    def test_main_option_region(self):
        self.make_env()
        self._test_main_region('--os-region-name=myregion bay-list',
                               'myregion')

    def test_main_env_region(self):
        fake_env = dict(utils.FAKE_ENV, OS_REGION_NAME='myregion')
        self.make_env(fake_env=fake_env)
        self._test_main_region('bay-list', 'myregion')

    def test_main_no_region(self):
        self.make_env()
        self._test_main_region('bay-list', None)

    @mock.patch('magnumclient.v1.client.Client')
    def test_main_endpoint_public(self, mock_client):
        self.make_env()
        self.shell('--endpoint-type publicURL bay-list')
        mock_client.assert_called_once_with(
            username='username', api_key='password',
            endpoint_type='publicURL', project_id='',
            project_name='tenant_name', auth_url=self.AUTH_URL,
            service_type='container', region_name=None,
            project_domain_id='', project_domain_name='',
            user_domain_id='', user_domain_name='',
            magnum_url=None, insecure=False)

    @mock.patch('magnumclient.v1.client.Client')
    def test_main_endpoint_internal(self, mock_client):
        self.make_env()
        self.shell('--endpoint-type internalURL bay-list')
        mock_client.assert_called_once_with(
            username='username', api_key='password',
            endpoint_type='internalURL', project_id='',
            project_name='tenant_name', auth_url=self.AUTH_URL,
            service_type='container', region_name=None,
            project_domain_id='', project_domain_name='',
            user_domain_id='', user_domain_name='',
            magnum_url=None, insecure=False)


class ShellTestKeystoneV3(ShellTest):
    AUTH_URL = 'http://no.where/v3'

    def make_env(self, exclude=None, fake_env=FAKE_ENV):
        if 'OS_AUTH_URL' in fake_env:
            fake_env.update({'OS_AUTH_URL': self.AUTH_URL})
        env = dict((k, v) for k, v in fake_env.items() if k != exclude)
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))

    def register_keystone_discovery_fixture(self, mreq):
        v3_url = "http://no.where/v3"
        v3_version = fixture.V3Discovery(v3_url)
        mreq.register_uri(
            'GET', v3_url, json=_create_ver_list([v3_version]),
            status_code=200)

    @mock.patch('magnumclient.v1.client.Client')
    def test_main_endpoint_public(self, mock_client):
        self.make_env(fake_env=FAKE_ENV4)
        self.shell('--endpoint-type publicURL bay-list')
        mock_client.assert_called_once_with(
            username='username', api_key='password',
            endpoint_type='publicURL', project_id='tenant_id',
            project_name='', auth_url=self.AUTH_URL,
            service_type='container', region_name=None,
            project_domain_id='', project_domain_name='Default',
            user_domain_id='', user_domain_name='Default',
            magnum_url=None, insecure=False)
