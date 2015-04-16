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

import mock
from testtools import matchers

from magnumclient import exceptions
from magnumclient.tests import utils

FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where/v2.0',
            'BYPASS_URL': 'http://magnum'}


class TestCommandLineArgument(utils.TestCase):
    _unrecognized_arg_error = [
        '.*?^usage: ',
        '.*?^error: unrecognized arguments:',
        ".*?^Try 'magnum help ' for more information.",
        ]

    _mandatory_arg_error = [
        '.*?^usage: ',
        '.*?^error: argument',
        ".*?^Try 'magnum help ",
        ]

    _few_argument_error = [
        '.*?^usage: magnum ',
        '.*?^error: too few arguments',
        ".*?^Try"
        ]

    def setUp(self):
        super(TestCommandLineArgument, self).setUp()
        self.make_env(fake_env=FAKE_ENV)
        keystone_mock = mock.patch(
            'magnumclient.v1.client.Client.get_keystone_client')
        keystone_mock.start()
        self.addCleanup(keystone_mock.stop)

    def _test_arg_success(self, command):
        stdout, stderr = self.shell(command)

    def _test_arg_failure(self, command, error_msg):
        stdout, stderr = self.shell(command, (2,))
        for line in error_msg:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(line,
                            re.DOTALL | re.MULTILINE))

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_success(self, mock_list):
        self._test_arg_success('bay-list')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.list')
    def test_bay_list_failure(self, mock_list):
        self._test_arg_failure('bay-list --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_success(self, mock_create, mock_get):
        self._test_arg_success('bay-create --name test --baymodel xxx '
                               '--node-count 123')
        self.assertTrue(mock_create.called)

        self._test_arg_success('bay-create --baymodel xxx')
        self.assertTrue(mock_create.called)

        self._test_arg_success('bay-create --name test --baymodel xxx')
        self.assertTrue(mock_create.called)

        self._test_arg_success('bay-create --baymodel xxx --node-count 123')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_success_only_baymodel_arg(self, mock_create, mock_get):
        self._test_arg_success('bay-create --baymodel xxx')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_only_name(self, mock_create):
        self._test_arg_failure('bay-create --name test',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_only_node_count(self, mock_create):
        self._test_arg_failure('bay-create --node-count 1',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.create')
    def test_bay_create_failure_no_arg(self, mock_create):
        self._test_arg_failure('bay-create',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.delete')
    def test_bay_delete_success(self, mock_delete):
        self._test_arg_success('bay-delete xxx')
        self.assertTrue(mock_delete.called)
        self.assertEqual(1, mock_delete.call_count)

    @mock.patch('magnumclient.v1.bays.BayManager.delete')
    def test_bay_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('bay-delete xxx xyz')
        self.assertTrue(mock_delete.called)
        self.assertEqual(2, mock_delete.call_count)

    @mock.patch('magnumclient.v1.bays.BayManager.delete')
    def test_bay_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('bay-delete', self._few_argument_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_show_success(self, mock_show):
        self._test_arg_success('bay-show xxx')
        self.assertTrue(mock_show.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    def test_bay_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('bay-show', self._few_argument_error)
        self.assertFalse(mock_show.called)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_success(self, mock_update):
        self._test_arg_success('bay-update test add test=test')
        self.assertTrue(mock_update.called)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_success_many_attribute(self, mock_update):
        self._test_arg_success('bay-update test add test=test test1=test1')
        self.assertTrue(mock_update.called)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_failure_wrong_op(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum bay-update ',
            '.*?^error: argument <op>: invalid choice: ',
            ".*?^Try 'magnum help bay-update' for more information."
            ]
        self._test_arg_failure('bay-update test wrong test=test', _error_msg)
        self.assertFalse(mock_update.called)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_failure_wrong_attribute(self, mock_update):
        _error_msg = [
            '.*?^ERROR: Attributes must be a list of PATH=VALUE'
            ]
        self.assertRaises(exceptions.CommandError, self._test_arg_failure,
                          'bay-update test add test', _error_msg)
        self.assertFalse(mock_update.called)

    @mock.patch('magnumclient.v1.bays.BayManager.update')
    def test_bay_update_failure_few_args(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum bay-update ',
            '.*?^error: too few arguments',
            ".*?^Try 'magnum help bay-update' for more information."
            ]
        self._test_arg_failure('bay-update', _error_msg)
        self.assertFalse(mock_update.called)

        self._test_arg_failure('bay-update test', _error_msg)
        self.assertFalse(mock_update.called)

        self._test_arg_failure('bay-update test add', _error_msg)
        self.assertFalse(mock_update.called)

    # baymodel commands

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.create')
    def test_baymodel_create_success(self, mock_create):
        self._test_arg_success('baymodel-create '
                               '--name test '
                               '--image-id test_image '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--dns-nameserver test_dns '
                               '--flavor-id test_flavor '
                               '--fixed-network public '
                               '--master-flavor-id test_flavor '
                               '--docker-volume-size 10')
        self.assertTrue(mock_create.called)

        self._test_arg_success('baymodel-create '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--name test ')

        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.create')
    def test_baymodel_create_success_with_master_flavor(self, mock_create):
        self._test_arg_success('baymodel-create '
                               '--name test '
                               '--image-id test_image '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--dns-nameserver test_dns '
                               '--master-flavor-id test_flavor')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.create')
    def test_baymodel_create_docker_vol_size_success(self, mock_create):
        self._test_arg_success('baymodel-create '
                               '--name test --docker-volume-size 4514 '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               )
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.create')
    def test_baymodel_create_fixed_network_success(self, mock_create):
        self._test_arg_success('baymodel-create '
                               '--name test --fixed-network private '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image ')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.create')
    def test_baymodel_create_ssh_authorized_key_success(self, mock_create):
        self._test_arg_success('baymodel-create '
                               '--name test '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--ssh-authorized-key test_key '
                               )
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.create')
    def test_baymodel_create_failure_few_arg(self, mock_create):
        self._test_arg_failure('baymodel-create '
                               '--name test', self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

        self._test_arg_failure('baymodel-create '
                               '--image-id test', self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

        self._test_arg_failure('baymodel-create '
                               '--keypair-id test', self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

        self._test_arg_failure('baymodel-create '
                               '--external-network-id test',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

        self._test_arg_failure('baymodel-create', self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    def test_baymodel_show_success(self, mock_show):
        self._test_arg_success('baymodel-show xxx')
        self.assertTrue(mock_show.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.get')
    def test_baymodel_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('baymodel-show', self._few_argument_error)
        self.assertFalse(mock_show.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.delete')
    def test_baymodel_delete_success(self, mock_delete):
        self._test_arg_success('baymodel-delete xxx')
        self.assertTrue(mock_delete.called)
        self.assertEqual(1, mock_delete.call_count)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.delete')
    def test_baymodel_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('baymodel-delete xxx xyz')
        self.assertTrue(mock_delete.called)
        self.assertEqual(2, mock_delete.call_count)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.delete')
    def test_baymodel_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('baymodel-delete', self._few_argument_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.list')
    def test_baymodel_list_success(self, mock_list):
        self._test_arg_success('baymodel-list')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.baymodels.BayModelManager.list')
    def test_baymodel_list_failure(self, mock_list):
        self._test_arg_failure('baymodel-list --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.nodes.NodeManager.list')
    def test_node_list_success(self, mock_list):
        self._test_arg_success('node-list')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.nodes.NodeManager.list')
    def test_node_list_failure(self, mock_list):
        self._test_arg_failure('node-list --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.nodes.NodeManager.create')
    def test_node_create_success(self, mock_create):
        self._test_arg_success('node-create '
                               '--type test '
                               '--image-id test')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.pods.PodManager.list')
    def test_pod_list_success(self, mock_list):
        self._test_arg_success('pod-list')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.pods.PodManager.list')
    def test_pod_list_failure(self, mock_list):
        self._test_arg_failure('pod-list --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.pods.PodManager.create')
    def test_pod_create_success(self, mock_list, mock_get):
        self._test_arg_success('pod-create '
                               '--bay xxx '
                               '--manifest test '
                               '--manifest-url test_url')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.pods.PodManager.create')
    def test_pod_create_failure_few_arg(self, mock_list, mock_get):
        self._test_arg_failure('pod-create '
                               '--manifest test '
                               '--manifest-url test_url',
                               self._mandatory_arg_error)
        self.assertFalse(mock_list.called)

        self._test_arg_failure('pod-create '
                               'bay xxx '
                               '--manifest-url test_url',
                               self._mandatory_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.pods.PodManager.delete')
    def test_pod_delete_success(self, mock_delete):
        self._test_arg_success('pod-delete xxx')
        self.assertTrue(mock_delete.called)
        self.assertEqual(1, mock_delete.call_count)

    @mock.patch('magnumclient.v1.pods.PodManager.delete')
    def test_pod_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('pod-delete xxx xyz')
        self.assertTrue(mock_delete.called)
        self.assertEqual(2, mock_delete.call_count)

    @mock.patch('magnumclient.v1.pods.PodManager.delete')
    def test_pod_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('pod-delete', self._few_argument_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.pods.PodManager.get')
    def test_pod_show_success(self, mock_show):
        self._test_arg_success('pod-show xxx')
        self.assertTrue(mock_show.called)

    @mock.patch('magnumclient.v1.pods.PodManager.get')
    def test_pod_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('pod-show', self._few_argument_error)
        self.assertFalse(mock_show.called)

    @mock.patch('magnumclient.v1.replicationcontrollers.'
                'ReplicationControllerManager.list')
    def test_rc_list_success(self, mock_list):
        self._test_arg_success('rc-list')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.replicationcontrollers.'
                'ReplicationControllerManager.list')
    def test_rc_list_failure(self, mock_list):
        self._test_arg_failure('rc-list --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.replicationcontrollers.'
                'ReplicationControllerManager.create')
    def test_rc_create_success(self, mock_create, mock_get):
        self._test_arg_success('rc-create '
                               '--bay xxx '
                               '--manifest test '
                               '--manifest-url test_url')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.replicationcontrollers.'
                'ReplicationControllerManager.create')
    def test_rc_create_failure_few_arg(self, mock_create, mock_get):
        self._test_arg_failure('rc-create '
                               '--manifest test '
                               '--manifest-url test_url',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

        self._test_arg_failure('rc-create '
                               'bay xxx '
                               '--manifest-url test_url',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.replicationcontrollers.'
                'ReplicationControllerManager.delete')
    def test_rc_delete_success(self, mock_delete):
        self._test_arg_success('rc-delete xxx')
        self.assertTrue(mock_delete.called)

    @mock.patch('magnumclient.v1.replicationcontrollers.'
                'ReplicationControllerManager.delete')
    def test_rc_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('rc-delete xxx xyz')
        self.assertTrue(mock_delete.called)
        self.assertEqual(2, mock_delete.call_count)

    @mock.patch('magnumclient.v1.replicationcontrollers.'
                'ReplicationControllerManager.delete')
    def test_rc_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('rc-delete', self._few_argument_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.replicationcontrollers.'
                'ReplicationControllerManager.get')
    def test_rc_show_success(self, mock_show):
        self._test_arg_success('rc-show xxx')
        self.assertTrue(mock_show.called)

    @mock.patch('magnumclient.v1.replicationcontrollers.'
                'ReplicationControllerManager.get')
    def test_rc_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('rc-show', self._few_argument_error)
        self.assertFalse(mock_show.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.list')
    def test_service_list_success(self, mock_list):
        self._test_arg_success('service-list')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.list')
    def test_service_list_failure(self, mock_list):
        self._test_arg_failure('service-list --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    @mock.patch('magnumclient.v1.bays.BayManager.get')
    @mock.patch('magnumclient.v1.services.ServiceManager.create')
    def test_service_create_success(self, mock_create, mock_get):
        self._test_arg_success('service-create '
                               '--bay xxx '
                               '--manifest test '
                               '--manifest-url test_url')
        self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.create')
    def test_service_create_failure_few_arg(self, mock_create):
        self._test_arg_failure('service-create '
                               '--manifest test '
                               '--manifest-url test_url',
                               self._mandatory_arg_error)
        self.assertFalse(mock_create.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.delete')
    def test_service_delete_success(self, mock_delete):
        self._test_arg_success('service-delete xxx')
        self.assertTrue(mock_delete.called)
        self.assertEqual(1, mock_delete.call_count)

    @mock.patch('magnumclient.v1.services.ServiceManager.delete')
    def test_service_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('service-delete xxx xyz')
        self.assertTrue(mock_delete.called)
        self.assertEqual(2, mock_delete.call_count)

    @mock.patch('magnumclient.v1.services.ServiceManager.delete')
    def test_service_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('service-delete', self._few_argument_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.get')
    def test_service_show_success(self, mock_show):
        self._test_arg_success('service-show xxx')
        self.assertTrue(mock_show.called)

    @mock.patch('magnumclient.v1.services.ServiceManager.get')
    def test_service_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('service-show', self._few_argument_error)
        self.assertFalse(mock_show.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.list')
    def test_container_list_success(self, mock_list):
        self._test_arg_success('container-list')
        self.assertTrue(mock_list.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.list')
    def test_container_list_failure(self, mock_list):
        self._test_arg_failure('container-list --wrong',
                               self._unrecognized_arg_error)
        self.assertFalse(mock_list.called)

    # NOTE(madhuri) Skip test because of command failure
    # @mock.patch('magnumclient.v1.containers.ContainerManager.create')
    # def test_container_create_success(self, mock_create):
    #    self._test_arg_success('container-create '
    #                           '--json test')
    #    self.assertTrue(mock_create.called)

    #    self._test_arg_success('container-creat')
    #    self.assertTrue(mock_create.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.delete')
    def test_container_delete_success(self, mock_delete):
        self._test_arg_success('container-delete xxx')
        self.assertTrue(mock_delete.called)
        self.assertEqual(1, mock_delete.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.delete')
    def test_container_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('container-delete xxx xyz')
        self.assertTrue(mock_delete.called)
        self.assertEqual(2, mock_delete.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.delete')
    def test_container_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('container-delete', self._few_argument_error)
        self.assertFalse(mock_delete.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.get')
    def test_container_show_success(self, mock_show):
        self._test_arg_success('container-show xxx')
        self.assertTrue(mock_show.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.get')
    def test_container_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('container-show', self._few_argument_error)
        self.assertFalse(mock_show.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.reboot')
    def test_container_reboot_success(self, mock_reboot):
        self._test_arg_success('container-reboot xxx')
        self.assertTrue(mock_reboot.called)
        self.assertEqual(1, mock_reboot.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.reboot')
    def test_container_reboot_multiple_id_success(self, mock_reboot):
        self._test_arg_success('container-reboot xxx xyz')
        self.assertTrue(mock_reboot.called)
        self.assertEqual(2, mock_reboot.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.reboot')
    def test_container_reboot_failure_no_arg(self, mock_reboot):
        self._test_arg_failure('container-reboot', self._few_argument_error)
        self.assertFalse(mock_reboot.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.stop')
    def test_container_stop_success(self, mock_stop):
        self._test_arg_success('container-stop xxx')
        self.assertTrue(mock_stop.called)
        self.assertEqual(1, mock_stop.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.stop')
    def test_container_stop_multiple_id_success(self, mock_stop):
        self._test_arg_success('container-stop xxx xyz')
        self.assertTrue(mock_stop.called)
        self.assertEqual(2, mock_stop.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.stop')
    def test_container_stop_failure_no_arg(self, mock_stop):
        self._test_arg_failure('container-stop', self._few_argument_error)
        self.assertFalse(mock_stop.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.start')
    def test_container_start_success(self, mock_start):
        self._test_arg_success('container-start xxx')
        self.assertTrue(mock_start.called)
        self.assertEqual(1, mock_start.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.start')
    def test_container_start_multiple_id_success(self, mock_start):
        self._test_arg_success('container-start xxx xyz')
        self.assertTrue(mock_start.called)
        self.assertEqual(2, mock_start.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.start')
    def test_container_start_failure_no_arg(self, mock_start):
        self._test_arg_failure('container-start', self._few_argument_error)
        self.assertFalse(mock_start.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.pause')
    def test_container_pause_success(self, mock_pause):
        self._test_arg_success('container-pause xxx')
        self.assertTrue(mock_pause.called)
        self.assertEqual(1, mock_pause.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.pause')
    def test_container_multiple_id_pause_success(self, mock_pause):
        self._test_arg_success('container-pause xxx xyz')
        self.assertTrue(mock_pause.called)
        self.assertEqual(2, mock_pause.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.pause')
    def test_container_pause_failure_no_arg(self, mock_pause):
        self._test_arg_failure('container-pause', self._few_argument_error)
        self.assertFalse(mock_pause.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.unpause')
    def test_container_unpause_success(self, mock_unpause):
        self._test_arg_success('container-unpause xxx')
        self.assertTrue(mock_unpause.called)
        self.assertEqual(1, mock_unpause.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.unpause')
    def test_container_unpause_multiple_id_success(self, mock_unpause):
        self._test_arg_success('container-unpause xxx xyz')
        self.assertTrue(mock_unpause.called)
        self.assertEqual(2, mock_unpause.call_count)

    @mock.patch('magnumclient.v1.containers.ContainerManager.unpause')
    def test_container_unpause_failure_no_arg(self, mock_unpause):
        self._test_arg_failure('container-unpause', self._few_argument_error)
        self.assertFalse(mock_unpause.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.logs')
    def test_container_logs_success(self, mock_logs):
        self._test_arg_success('container-logs xxx')
        self.assertTrue(mock_logs.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.logs')
    def test_container_logs_failure_no_arg(self, mock_logs):
        self._test_arg_failure('container-logs', self._few_argument_error)
        self.assertFalse(mock_logs.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.execute')
    def test_container_execute_success(self, mock_execute):
        self._test_arg_success('container-execute xxx '
                               '--command ls')
        self.assertTrue(mock_execute.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.execute')
    def test_container_execute_failure_no_option(self, mock_execute):
        self._test_arg_failure('container-execute xxx',
                               self._mandatory_arg_error)
        self.assertFalse(mock_execute.called)

        self._test_arg_failure('container-execute --command ls',
                               self._few_argument_error)
        self.assertFalse(mock_execute.called)

    @mock.patch('magnumclient.v1.containers.ContainerManager.execute')
    def test_container_execute_failure_no_arg(self, mock_execute):
        self._test_arg_failure('container-execute', self._few_argument_error)
        self.assertFalse(mock_execute.called)
