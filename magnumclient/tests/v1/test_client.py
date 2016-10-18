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

from keystoneauth1.exceptions import catalog

from magnumclient.v1 import client


class ClientInitializeTest(testtools.TestCase):

    def _load_session_kwargs(self):
        return {
            'username': None,
            'project_id': None,
            'project_name': None,
            'auth_url': None,
            'password': None,
            'auth_type': 'password',
            'insecure': False,
            'user_domain_id': None,
            'user_domain_name': None,
            'project_domain_id': None,
            'project_domain_name': None,
            'auth_token': None,
            'timeout': 600,
        }

    def _load_service_type_kwargs(self):
        return {
            'interface': 'public',
            'region_name': None,
            'service_name': None,
            'service_type': 'container-infra',
        }

    def _session_client_kwargs(self, session):
        kwargs = self._load_service_type_kwargs()
        kwargs['endpoint_override'] = None
        kwargs['session'] = session
        kwargs['api_version'] = None

        return kwargs

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('magnumclient.v1.client._load_session')
    @mock.patch('magnumclient.v1.client._load_service_type',
                return_value='container-infra')
    def test_init_with_session(self,
                               mock_load_service_type,
                               mock_load_session,
                               mock_http_client):
        session = mock.Mock()
        client.Client(session=session)
        mock_load_session.assert_not_called()
        mock_load_service_type.assert_called_once_with(
            session,
            **self._load_service_type_kwargs()
        )
        mock_http_client.assert_called_once_with(
            **self._session_client_kwargs(session)
        )

    def _test_init_with_secret(self,
                               init_func,
                               mock_load_service_type,
                               mock_load_session,
                               mock_http_client,):
        expected_password = 'expected_password'
        session = mock.Mock()
        mock_load_session.return_value = session
        init_func(expected_password)
        load_session_args = self._load_session_kwargs()
        load_session_args['password'] = expected_password
        mock_load_session.assert_called_once_with(
            **load_session_args
        )
        mock_load_service_type.assert_called_once_with(
            session,
            **self._load_service_type_kwargs()
        )
        mock_http_client.assert_called_once_with(
            **self._session_client_kwargs(session)
        )

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('magnumclient.v1.client._load_session')
    @mock.patch('magnumclient.v1.client._load_service_type',
                return_value='container-infra')
    def test_init_with_password(self,
                                mock_load_service_type,
                                mock_load_session,
                                mock_http_client):
        self._test_init_with_secret(
            lambda x: client.Client(password=x),
            mock_load_service_type,
            mock_load_session,
            mock_http_client
        )

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('magnumclient.v1.client._load_session')
    @mock.patch('magnumclient.v1.client._load_service_type',
                return_value='container-infra')
    def test_init_with_api_key(self,
                               mock_load_service_type,
                               mock_load_session,
                               mock_http_client):
        self._test_init_with_secret(
            lambda x: client.Client(api_key=x),
            mock_load_service_type,
            mock_load_session,
            mock_http_client
        )

    @mock.patch('magnumclient.common.httpclient.HTTPClient')
    def test_init_with_auth_token(self,
                                  mock_http_client,):
        expected_token = 'expected_password'
        expected_magnum_url = 'expected_magnum_url'
        expected_api_version = 'expected_api_version'
        expected_insecure = False
        expected_timeout = 600
        expected_kwargs = {'expected_key': 'expected_value'}
        client.Client(auth_token=expected_token,
                      magnum_url=expected_magnum_url,
                      api_version=expected_api_version,
                      timeout=expected_timeout,
                      insecure=expected_insecure,
                      **expected_kwargs)

        mock_http_client.assert_called_once_with(
            expected_magnum_url,
            token=expected_token,
            api_version=expected_api_version,
            timeout=expected_timeout,
            insecure=expected_insecure,
            **expected_kwargs)

    def _test_init_with_interface(self,
                                  init_func,
                                  mock_load_service_type,
                                  mock_load_session,
                                  mock_http_client):
        expected_interface = 'admin'
        session = mock.Mock()
        mock_load_session.return_value = session
        init_func(expected_interface)
        mock_load_session.assert_called_once_with(
            **self._load_session_kwargs()
        )
        expected_kwargs = self._load_service_type_kwargs()
        expected_kwargs['interface'] = expected_interface
        mock_load_service_type.assert_called_once_with(
            session,
            **expected_kwargs
        )
        expected_kwargs = self._session_client_kwargs(session)
        expected_kwargs['interface'] = expected_interface
        mock_http_client.assert_called_once_with(
            **expected_kwargs
        )

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('magnumclient.v1.client._load_session')
    @mock.patch('magnumclient.v1.client._load_service_type',
                return_value='container-infra')
    def test_init_with_interface(self,
                                 mock_load_service_type,
                                 mock_load_session,
                                 mock_http_client):
        self._test_init_with_interface(
            lambda x: client.Client(interface=x),
            mock_load_service_type,
            mock_load_session,
            mock_http_client
        )

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('magnumclient.v1.client._load_session')
    @mock.patch('magnumclient.v1.client._load_service_type',
                return_value='container-infra')
    def test_init_with_endpoint_type(self,
                                     mock_load_service_type,
                                     mock_load_session,
                                     mock_http_client):
        self._test_init_with_interface(
            lambda x: client.Client(interface='public',
                                    endpoint_type=('%sURL' % x)),
            mock_load_service_type,
            mock_load_session,
            mock_http_client
        )

    @mock.patch('magnumclient.common.httpclient.SessionClient')
    @mock.patch('magnumclient.v1.client._load_session')
    def test_init_with_legacy_service_type(self,
                                           mock_load_session,
                                           mock_http_client):
        session = mock.Mock()
        mock_load_session.return_value = session
        session.get_endpoint.side_effect = [
            catalog.EndpointNotFound(),
            mock.Mock()
        ]
        client.Client(username='myuser', auth_url='authurl')
        expected_kwargs = self._session_client_kwargs(session)
        expected_kwargs['service_type'] = 'container'
        mock_http_client.assert_called_once_with(
            **expected_kwargs
        )
