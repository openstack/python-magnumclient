# Copyright (c) 2015 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock
import testtools

from magnumclient import client


class ClientTest(testtools.TestCase):

    @mock.patch('magnumclient.v1.client.Client')
    def test_no_version_argument(self, mock_magnum_client):
        client.Client(auth_token='mytoken', magnum_url='http://myurl/')
        mock_magnum_client.assert_called_with(
            auth_token='mytoken', magnum_url='http://myurl/')

    @mock.patch('magnumclient.v1.client.Client')
    def test_valid_version_argument(self, mock_magnum_client):
        client.Client(version='1', magnum_url='http://myurl/')
        mock_magnum_client.assert_called_with(magnum_url='http://myurl/')

    @mock.patch('magnumclient.v1.client.Client')
    def test_invalid_version_argument(self, mock_magnum_client):
        self.assertRaises(
            ValueError,
            client.Client, version='2', magnum_url='http://myurl/')
