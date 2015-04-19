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

    @mock.patch('magnumclient.common.httpclient.HTTPClient')
    @mock.patch.object(client.Client, 'get_keystone_client')
    def test_init_with_token_and_url(self, keystone_client, http_client):
        client.Client(input_auth_token='mytoken', magnum_url='http://myurl/')
        self.assertFalse(keystone_client.called)
        http_client.assert_called_once_with(
            'http://myurl/', token='mytoken', auth_ref=None)

    @mock.patch('magnumclient.common.httpclient.HTTPClient')
    @mock.patch.object(client.Client, 'get_keystone_client')
    def test_init_with_token(self, keystone_client, http_client):
        mocked = mock.Mock()
        mocked.service_catalog.url_for.return_value = 'http://myurl/'
        keystone_client.return_value = mocked

        client.Client(input_auth_token='mytoken', auth_url='authurl')
        keystone_client.assert_called_once_with(
            token='mytoken', username=None, api_key=None,
            project_name=None, project_id=None,
            auth_url='authurl')
        http_client.assert_called_once_with(
            'http://myurl/', token='mytoken', auth_ref=None)

    @mock.patch('magnumclient.common.httpclient.HTTPClient')
    @mock.patch.object(client.Client, 'get_keystone_client')
    def test_init_with_user(self, keystone_client, http_client):
        mocked = mock.Mock()
        mocked.auth_token = 'mytoken'
        mocked.service_catalog.url_for.return_value = 'http://myurl/'
        keystone_client.return_value = mocked

        client.Client(username='user', api_key='pass', project_name='prj',
                      auth_url='authurl')
        keystone_client.assert_called_once_with(
            username='user', api_key='pass',
            project_name='prj', project_id=None,
            auth_url='authurl')
        http_client.assert_called_once_with(
            'http://myurl/', token='mytoken', auth_ref=None)

    @mock.patch.object(client.Client, 'get_keystone_client')
    def test_init_unauthorized(self, keystone_client):
        mocked = mock.Mock()
        mocked.auth_token = None
        keystone_client.return_value = mocked

        self.assertRaises(
            RuntimeError, client.Client,
            username='user', api_key='pass', project_name='prj',
            auth_url='authurl')

    def _test_get_keystone_client(self, auth_url, keystone_client):
        client.Client.get_keystone_client(
            username='user', api_key='pass', project_name='prj',
            auth_url=auth_url)
        self.assertTrue(keystone_client.called)

    @mock.patch('keystoneclient.v2_0.client.Client')
    def test_get_keystone_client_v2(self, keystone_client):
        self._test_get_keystone_client(
            'http://authhost/v2.0', keystone_client)

    @mock.patch('keystoneclient.v3.client.Client')
    def test_get_keystone_client_v3(self, keystone_client):
        self._test_get_keystone_client(
            'http://authhost/v3', keystone_client)

    def test_get_keystone_client_no_url(self):
        self.assertRaises(RuntimeError,
                          self._test_get_keystone_client,
                          None, None)
