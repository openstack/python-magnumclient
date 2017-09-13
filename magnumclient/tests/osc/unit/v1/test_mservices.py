# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import mock

from magnumclient.osc.v1 import mservices
from magnumclient.tests.osc.unit.v1 import fakes


class TestServiceList(fakes.TestMagnumClientOSCV1):
    columns = ('id', 'host', 'binary', 'state', 'disabled',
               'disabled_reason', 'created_at', 'updated_at')

    def setUp(self):
        super(TestServiceList, self).setUp()
        self.mservices_mock = self.app.client_manager.container_infra.mservices
        self.mservices_mock.list = mock.Mock()
        fake_service = mock.Mock(
            Binary='magnum-conductor',
            Host='Host1',
            Status='enabled',
            State='up',
            Updated_at=None,
            Disabled_Reason=None,
        )
        fake_service.name = 'test_service'
        self.mservices_mock.list.return_value = [fake_service]

        # Get the command object to test
        self.cmd = mservices.ListService(self.app, None)

    def test_service_list(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mservices_mock.list.assert_called_with()
        self.assertEqual(self.columns, columns)
