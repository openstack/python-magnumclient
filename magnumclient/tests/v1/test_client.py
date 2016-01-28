# Copyright (c) 2015 Thales Services SAS
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
import testtools

from magnumclient.v1 import client


class ClientTest(testtools.TestCase):

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('keystoneauth1.session.Session')
    def test_init_with_session(self, mock_session, http_client):
        session = mock.Mock()
        client.Client(session=session)
        mock_session.assert_not_called()
        http_client.assert_called_once_with(
            interface='public',
            region_name=None,
            service_name=None,
            service_type='container',
            session=session)

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('keystoneauth1.token_endpoint.Token')
    @mock.patch('keystoneauth1.session.Session')
    def test_init_with_token_and_url(
            self, mock_session, mock_token, http_client):
        mock_auth_plugin = mock.Mock()
        mock_token.return_value = mock_auth_plugin
        session = mock.Mock()
        mock_session.return_value = session
        client.Client(input_auth_token='mytoken', magnum_url='http://myurl/')
        mock_session.assert_called_once_with(
            auth=mock_auth_plugin, verify=True)
        http_client.assert_called_once_with(
            endpoint_override='http://myurl/',
            interface='public',
            region_name=None,
            service_name=None,
            service_type='container',
            session=session)

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('keystoneauth1.loading.get_plugin_loader')
    @mock.patch('keystoneauth1.session.Session')
    def test_init_with_token(
            self, mock_session, mock_loader, http_client):
        mock_plugin = mock.Mock()
        mock_loader.return_value = mock_plugin
        client.Client(input_auth_token='mytoken', auth_url='authurl')
        mock_loader.assert_called_once_with('token')
        mock_plugin.load_from_options.assert_called_once_with(
            auth_url='authurl',
            project_id=None,
            project_name=None,
            project_domain_id=None,
            project_domain_name=None,
            user_domain_id=None,
            user_domain_name=None,
            token='mytoken')
        http_client.assert_called_once_with(
            interface='public',
            region_name=None,
            service_name=None,
            service_type='container',
            session=mock.ANY)

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('keystoneauth1.loading.get_plugin_loader')
    @mock.patch('keystoneauth1.session.Session')
    def test_init_with_user(
            self, mock_session, mock_loader, http_client):
        mock_plugin = mock.Mock()
        mock_loader.return_value = mock_plugin
        client.Client(username='myuser', auth_url='authurl')
        mock_loader.assert_called_once_with('password')
        mock_plugin.load_from_options.assert_called_once_with(
            auth_url='authurl',
            username='myuser',
            password=None,
            project_domain_id=None,
            project_domain_name=None,
            user_domain_id=None,
            user_domain_name=None,
            project_id=None,
            project_name=None)
        http_client.assert_called_once_with(
            interface='public',
            region_name=None,
            service_name=None,
            service_type='container',
            session=mock.ANY)

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('keystoneauth1.loading.get_plugin_loader')
    @mock.patch('keystoneauth1.session.Session')
    def test_init_unauthorized(
            self, mock_session, mock_loader, http_client):
        mock_plugin = mock.Mock()
        mock_loader.return_value = mock_plugin
        mock_session_obj = mock.Mock()
        mock_session.return_value = mock_session_obj
        mock_session_obj.get_endpoint.side_effect = Exception()
        self.assertRaises(
            RuntimeError,
            client.Client, username='myuser', auth_url='authurl')
        mock_loader.assert_called_once_with('password')
        mock_plugin.load_from_options.assert_called_once_with(
            auth_url='authurl',
            username='myuser',
            password=None,
            project_domain_id=None,
            project_domain_name=None,
            user_domain_id=None,
            user_domain_name=None,
            project_id=None,
            project_name=None)
        http_client.assert_not_called()
