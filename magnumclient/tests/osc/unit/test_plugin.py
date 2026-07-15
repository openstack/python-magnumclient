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

from unittest import mock

import testtools

from magnumclient.osc import plugin


class TestMakeClient(testtools.TestCase):

    def _make_instance(self, api_version):
        instance = mock.Mock()
        instance._api_version = {'container_infra': api_version}
        return instance

    def _call_make_client(self, api_version):
        instance = self._make_instance(api_version)
        with mock.patch('osc_lib.utils.get_client_class') as mock_gcc:
            mock_client_class = mock.Mock(return_value=mock.Mock())
            mock_gcc.return_value = mock_client_class
            plugin.make_client(instance)
            return mock_gcc, mock_client_class

    def test_major_version_uses_latest(self):
        """Bare major version '1' results in api_version='latest'."""
        mock_gcc, mock_client_class = self._call_make_client('1')
        mock_gcc.assert_called_once_with('container_infra', '1', mock.ANY)
        _, kwargs = mock_client_class.call_args
        self.assertEqual('latest', kwargs['api_version'])

    def test_microversion_forwarded(self):
        """Full microversion '1.12' is forwarded to the HTTP client."""
        mock_gcc, mock_client_class = self._call_make_client('1.12')
        # Major part must be used for the class lookup
        mock_gcc.assert_called_once_with('container_infra', '1', mock.ANY)
        # Full microversion must reach the HTTP client
        _, kwargs = mock_client_class.call_args
        self.assertEqual('1.12', kwargs['api_version'])
