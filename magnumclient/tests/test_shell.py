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

import argparse
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
            'OS_PROJECT_NAME': 'project_name',
            'OS_AUTH_URL': 'http://no.where/v2.0'}

FAKE_ENV2 = {'OS_USER_ID': 'user_id',
             'OS_PASSWORD': 'password',
             'OS_PROJECT_ID': 'project_id',
             'OS_AUTH_URL': 'http://no.where/v2.0'}

FAKE_ENV3 = {'OS_USERNAME': 'username',
             'OS_PASSWORD': 'password',
             'OS_PROJECT_ID': 'project_id',
             'OS_AUTH_URL': 'http://no.where/v2.0'}

FAKE_ENV4 = {'OS_USERNAME': 'username',
             'OS_PASSWORD': 'password',
             'OS_PROJECT_ID': 'project_id',
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

    _msg_no_tenant_project = ("You must provide a project name or project id"
                              " via --os-project-name, --os-project-id,"
                              " env[OS_PROJECT_NAME] or env[OS_PROJECT_ID]")

    def setUp(self):
        super(ShellTest, self).setUp()
        self.nc_util = mock.patch(
            'magnumclient.common.cliutils.isunauthenticated').start()
        self.nc_util.return_value = False

    def test_positive_non_zero_float(self):
        output = magnumclient.shell.positive_non_zero_float(None)
        self.assertIsNone(output)

        output = magnumclient.shell.positive_non_zero_float(5)
        self.assertEqual(5, output)

        output = magnumclient.shell.positive_non_zero_float(5.0)
        self.assertEqual(5.0, output)

        self.assertRaises(argparse.ArgumentTypeError,
                          magnumclient.shell.positive_non_zero_float,
                          "Invalid")

        self.assertRaises(argparse.ArgumentTypeError,
                          magnumclient.shell.positive_non_zero_float, -1)

        self.assertRaises(argparse.ArgumentTypeError,
                          magnumclient.shell.positive_non_zero_float, 0)

    def test_help_unknown_command(self):
        self.assertRaises(exceptions.CommandError, self.shell, 'help foofoo')

    def test_help(self):
        required = [
            '.*?^usage: ',
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
            '.*help',
            '.*bay-show',
            '.*--bay']
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_no_username(self):
        required = ('You must provide a username via'
                    ' either --os-username or via env[OS_USERNAME]')
        self.make_env(exclude='OS_USERNAME')
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    def test_no_user_id(self):
        required = ('You must provide a username via'
                    ' either --os-username or via env[OS_USERNAME]')
        self.make_env(exclude='OS_USER_ID', fake_env=FAKE_ENV2)
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    def test_no_project_name(self):
        required = self._msg_no_tenant_project
        self.make_env(exclude='OS_PROJECT_NAME')
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    def test_no_project_id(self):
        required = self._msg_no_tenant_project
        self.make_env(exclude='OS_PROJECT_ID', fake_env=FAKE_ENV3)
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    def test_no_password(self):
        required = ('You must provide a password via either --os-password, '
                    'env[OS_PASSWORD], or prompted response')
        self.make_env(exclude='OS_PASSWORD', fake_env=FAKE_ENV3)
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    def test_no_auth_url(self):
        required = ("You must provide an auth url via either "
                    "--os-auth-url or via env[OS_AUTH_URL]")
        self.make_env(exclude='OS_AUTH_URL')
        try:
            self.shell('bay-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
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
        self.assertEqual('container-infra', client_kwargs['service_type'])

    @mock.patch('magnumclient.v1.bays_shell.do_bay_list')
    @mock.patch('magnumclient.v1.client.ksa_session')
    def test_insecure(self, mock_session, mock_bay_list):
        self.make_env()
        self.shell('--insecure bay-list')
        _, session_kwargs = mock_session.Session.call_args_list[0]
        self.assertEqual(False, session_kwargs['verify'])

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

    def _expected_client_kwargs(self):
        return {
            'password': 'password', 'auth_token': None,
            'auth_url': self.AUTH_URL, 'profile': None,
            'cloud': None, 'interface': 'public',
            'insecure': False, 'magnum_url': None,
            'project_id': None, 'project_name': 'project_name',
            'project_domain_id': None, 'project_domain_name': None,
            'region_name': None, 'service_type': 'container-infra',
            'user_id': None, 'username': 'username',
            'user_domain_id': None, 'user_domain_name': None,
            'api_version': 'latest'
        }

    @mock.patch('magnumclient.v1.client.Client')
    def _test_main_region(self, command, expected_region_name, mock_client):
        self.shell(command)
        expected_args = self._expected_client_kwargs()
        expected_args['region_name'] = expected_region_name
        mock_client.assert_called_once_with(**expected_args)

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
        expected_args = self._expected_client_kwargs()
        expected_args['interface'] = 'public'
        mock_client.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.client.Client')
    def test_main_endpoint_internal(self, mock_client):
        self.make_env()
        self.shell('--endpoint-type internalURL bay-list')
        expected_args = self._expected_client_kwargs()
        expected_args['interface'] = 'internal'
        mock_client.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.client.Client')
    def test_main_os_cloud(self, mock_client):
        expected_cloud = 'default'
        self.shell('--os-cloud %s bay-list' % expected_cloud)
        expected_args = self._expected_client_kwargs()
        expected_args['cloud'] = expected_cloud
        expected_args['username'] = None
        expected_args['password'] = None
        expected_args['project_name'] = None
        expected_args['auth_url'] = None
        mock_client.assert_called_once_with(**expected_args)

    @mock.patch('magnumclient.v1.client.Client')
    def test_main_env_os_cloud(self, mock_client):
        expected_cloud = 'default'
        self.make_env(fake_env={'OS_CLOUD': expected_cloud})
        self.shell('bay-list')
        expected_args = self._expected_client_kwargs()
        expected_args['cloud'] = expected_cloud
        expected_args['username'] = None
        expected_args['password'] = None
        expected_args['project_name'] = None
        expected_args['auth_url'] = None
        mock_client.assert_called_once_with(**expected_args)


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
        expected_args = self._expected_client_kwargs()
        expected_args['interface'] = 'public'
        expected_args['project_id'] = 'project_id'
        expected_args['project_name'] = None
        expected_args['project_domain_name'] = 'Default'
        expected_args['user_domain_name'] = 'Default'
        mock_client.assert_called_once_with(**expected_args)
