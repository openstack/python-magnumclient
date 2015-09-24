# Copyright 2014 NEC Corporation.  All rights reserved.
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
from mock import mock_open

from magnumclient.common import utils as magnum_utils
from magnumclient.tests import base
from magnumclient.v1 import shell


class ShellTest(base.TestCase):

    def setUp(self):
        super(ShellTest, self).setUp()

    def test_do_bay_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        shell.do_bay_list(client_mock, args)
        client_mock.bays.list.assert_called_once_with()

    def test_do_bay_create(self):
        client_mock = mock.MagicMock()
        baymodel = mock.MagicMock()
        baymodel.uuid = 'uuid'
        client_mock.baymodels.get.return_value = baymodel

        args = mock.MagicMock()
        node_count = 1
        args.node_count = node_count
        args.master_count = None
        args.discovery_url = None
        name = "test_bay"
        args.name = name
        baymodel_id_or_name = "test_baymodel_id"
        args.baymodel = baymodel_id_or_name
        args.timeout = None

        shell.do_bay_create(client_mock, args)
        client_mock.bays.create.assert_called_once_with(
            name=name, node_count=node_count, baymodel_id=baymodel.uuid,
            discovery_url=None, bay_create_timeout=None, master_count=None)

    def test_do_bay_create_with_discovery_url(self):
        client_mock = mock.MagicMock()
        baymodel = mock.MagicMock()
        baymodel.uuid = 'uuid'
        client_mock.baymodels.get.return_value = baymodel

        args = mock.MagicMock()
        node_count = 1
        args.node_count = node_count
        args.master_count = None
        discovery_url = 'discovery_url'
        args.discovery_url = discovery_url
        name = "test_bay"
        args.name = name
        baymodel_id_or_name = "test_baymodel_id"
        args.baymodel = baymodel_id_or_name
        args.timeout = None

        shell.do_bay_create(client_mock, args)
        client_mock.bays.create.assert_called_once_with(
            name=name, node_count=node_count, baymodel_id=baymodel.uuid,
            discovery_url=discovery_url, bay_create_timeout=None,
            master_count=None)

    def test_do_bay_create_with_bay_create_timeout(self):
        client_mock = mock.MagicMock()
        baymodel = mock.MagicMock()
        baymodel.uuid = 'uuid'
        client_mock.baymodels.get.return_value = baymodel

        args = mock.MagicMock()
        node_count = 1
        args.node_count = node_count
        args.master_count = None
        name = "test_bay"
        args.name = name
        baymodel_id_or_name = "test_baymodel_id"
        args.baymodel = baymodel_id_or_name
        bay_create_timeout = 15
        args.timeout = bay_create_timeout
        args.discovery_url = None

        shell.do_bay_create(client_mock, args)
        client_mock.bays.create.assert_called_once_with(
            name=name, node_count=node_count, baymodel_id=baymodel.uuid,
            discovery_url=None, bay_create_timeout=bay_create_timeout,
            master_count=None)

    def test_do_bay_create_with_master_node_count(self):
        client_mock = mock.MagicMock()
        baymodel = mock.MagicMock()
        baymodel.uuid = 'uuid'
        client_mock.baymodels.get.return_value = baymodel

        args = mock.MagicMock()
        node_count = 1
        args.node_count = node_count
        master_count = 1
        args.master_count = master_count
        args.discovery_url = None
        name = "test_bay"
        args.name = name
        baymodel_id_or_name = "test_baymodel_id"
        args.baymodel = baymodel_id_or_name
        args.timeout = None

        shell.do_bay_create(client_mock, args)
        client_mock.bays.create.assert_called_once_with(
            name=name, node_count=node_count, baymodel_id=baymodel.uuid,
            discovery_url=None, bay_create_timeout=None, master_count=1)

    def test_do_bay_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        bay_id = 'id'
        args.bay = [bay_id]

        shell.do_bay_delete(client_mock, args)
        client_mock.bays.delete.assert_called_once_with(bay_id)

    def test_do_bay_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        bay_id = 'id'
        args.bay = bay_id

        shell.do_bay_show(client_mock, args)
        client_mock.bays.get.assert_called_once_with(bay_id)

    def test_do_bay_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        bay_id = 'id'
        args.bay = bay_id
        op = 'add'
        args.op = op
        attributes = 'node_count=2'
        args.attributes = attributes
        shell.magnum_utils.args_array_to_patch = mock.MagicMock()
        patch = [{'path': '/node_count', 'value': 2, 'op': 'add'}]
        shell.magnum_utils.args_array_to_patch.return_value = patch

        shell.do_bay_update(client_mock, args)
        client_mock.bays.update.assert_called_once_with(bay_id, patch)

    @mock.patch('os.path.isfile')
    def test_do_ca_show(self, mock_isfile):
        mock_isfile.return_value = True

        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = 'CREATE_COMPLETE'
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        bay_id_or_name = "xxx"
        args.bay = bay_id_or_name

        shell.do_ca_show(client_mock, args)

        client_mock.certificates.get.assert_called_once_with(
            bay_uuid=bay.uuid)

    @mock.patch('os.path.isfile')
    def test_do_ca_show_wrong_status(self, mock_isfile):
        mock_isfile.return_value = True

        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = 'XXX'
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        bay_id_or_name = "xxx"
        args.bay = bay_id_or_name

        shell.do_ca_show(client_mock, args)

        self.assertFalse(client_mock.certificates.get.called)

    @mock.patch('os.path.isfile')
    def test_do_ca_sign(self, mock_isfile):
        mock_isfile.return_value = True

        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = 'CREATE_COMPLETE'
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        bay_id_or_name = "xxx"
        args.bay = bay_id_or_name
        csr = "test_csr"
        args.csr = csr

        fake_csr = 'fake-csr'
        mock_o = mock_open(read_data=fake_csr)
        with mock.patch.object(shell, 'open', mock_o):
            shell.do_ca_sign(client_mock, args)

            mock_isfile.assert_called_once_with(csr)
            mock_o.assert_called_once_with(csr, 'r')
            client_mock.certificates.create.assert_called_once_with(
                csr=fake_csr, bay_uuid=bay.uuid)

    @mock.patch('os.path.isfile')
    def test_do_ca_sign_wrong_status(self, mock_isfile):
        mock_isfile.return_value = True

        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = 'XXX'
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        bay_id_or_name = "xxx"
        args.bay = bay_id_or_name
        csr = "test_csr"
        args.csr = csr

        fake_csr = 'fake-csr'
        mock_o = mock_open(read_data=fake_csr)
        with mock.patch.object(shell, 'open', mock_o):
            shell.do_ca_sign(client_mock, args)

            self.assertFalse(mock_isfile.called)
            self.assertFalse(mock_o.called)
            self.assertFalse(client_mock.certificates.create.called)

    @mock.patch('os.path.isfile')
    def test_do_ca_sign_not_file(self, mock_isfile):
        mock_isfile.return_value = False

        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = 'CREATE_COMPLETE'
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        bay_id_or_name = "xxx"
        args.bay = bay_id_or_name
        csr = "test_csr"
        args.csr = csr

        fake_csr = 'fake-csr'
        mock_o = mock_open(read_data=fake_csr)
        with mock.patch.object(shell, 'open', mock_o):
            shell.do_ca_sign(client_mock, args)

            mock_isfile.assert_called_once_with(csr)
            self.assertFalse(mock_o.called)
            self.assertFalse(client_mock.certificates.create.called)

    def test_do_baymodel_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        name = "test_baymodel"
        args.name = name
        image_id = "test_image"
        args.image_id = image_id
        flavor_id = "test_flavor"
        args.flavor_id = flavor_id
        master_flavor_id = "test_master_flavor"
        args.master_flavor_id = master_flavor_id
        keypair_id = "test_keypair"
        args.keypair_id = keypair_id
        external_network_id = "test_external_network_id"
        args.external_network_id = external_network_id
        dns_nameserver = "test_dns_nameserver"
        args.dns_nameserver = dns_nameserver
        docker_volume_size = "2051"
        args.docker_volume_size = docker_volume_size
        fixed_network = "private"
        args.fixed_network = fixed_network
        network_driver = "test_driver"
        args.network_driver = network_driver
        ssh_authorized_key = "test_key"
        args.ssh_authorized_key = ssh_authorized_key
        coe = 'swarm'
        args.coe = coe
        http_proxy = 'http_proxy'
        args.http_proxy = http_proxy
        https_proxy = 'https_proxy'
        args.https_proxy = 'https_proxy'
        no_proxy = 'no_proxy'
        args.no_proxy = no_proxy
        labels = ['key1=val1']
        args.labels = labels
        insecure = True
        args.insecure = insecure

        shell.do_baymodel_create(client_mock, args)
        client_mock.baymodels.create.assert_called_once_with(
            name=name, image_id=image_id, flavor_id=flavor_id,
            master_flavor_id=master_flavor_id, keypair_id=keypair_id,
            external_network_id=external_network_id,
            docker_volume_size=docker_volume_size,
            fixed_network=fixed_network, dns_nameserver=dns_nameserver,
            ssh_authorized_key=ssh_authorized_key, coe=coe,
            http_proxy=http_proxy, https_proxy=https_proxy,
            no_proxy=no_proxy, network_driver=network_driver,
            labels=magnum_utils.format_labels(labels),
            insecure=insecure)

    def test_do_baymodel_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        baymodel_id = 'id'
        args.baymodels = [baymodel_id]

        shell.do_baymodel_delete(client_mock, args)
        client_mock.baymodels.delete.assert_called_once_with(baymodel_id)

    def test_do_baymodel_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        baymodel_id = 'id'
        args.baymodel = baymodel_id

        shell.do_baymodel_show(client_mock, args)
        client_mock.baymodels.get.assert_called_once_with(baymodel_id)

    def test_do_baymodel_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        shell.do_baymodel_list(client_mock, args)
        client_mock.baymodels.list.assert_called_once_with()

    def test_do_node_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        shell.do_node_list(client_mock, args)
        client_mock.nodes.list.assert_called_once_with()

    def test_do_node_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        type = "test_type"
        args.type = type
        image_id = "test_image"
        args.image_id = image_id

        shell.do_node_create(client_mock, args)
        client_mock.nodes.create.assert_called_once_with(
            type=type, image_id=image_id)

    def test_do_pod_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        shell.do_pod_list(client_mock, args)
        client_mock.pods.list.assert_called_once_with()

    def test_do_pod_create(self):
        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = 'CREATE_COMPLETE'
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        manifest_url = "test_url"
        args.manifest_url = manifest_url
        bay_id_or_name = "xxx"
        args.bay = bay_id_or_name
        manifest = "test_manifest"
        args.manifest = manifest

        shell.do_pod_create(client_mock, args)
        client_mock.pods.create.assert_called_once_with(
            manifest_url=manifest_url, bay_uuid=bay.uuid)

    def test_do_pod_create_with_bay_in_wrong_status(self):
        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = 'XXX'
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        manifest_url = "test_url"
        args.manifest_url = manifest_url
        bay_id_or_name = "xxx"
        args.bay = bay_id_or_name
        manifest = "test_manifest"
        args.manifest = manifest

        shell.do_pod_create(client_mock, args)
        self.assertFalse(client_mock.pods.create.called)

    def test_do_pod_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        pod_id = 'id'
        args.pod = pod_id
        op = 'add'
        args.op = op
        attributes = "labels={'name': 'value'}"
        args.attributes = attributes
        shell.magnum_utils.args_array_to_patch = mock.MagicMock()
        patch = [{'path': '/labels', 'value': {'name': 'value'}, 'op': 'add'}]
        shell.magnum_utils.args_array_to_patch.return_value = patch

        shell.do_pod_update(client_mock, args)
        client_mock.pods.update.assert_called_once_with(pod_id, patch)

    def test_do_pod_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        pod_id = 'id'
        args.pods = [pod_id]

        shell.do_pod_delete(client_mock, args)
        client_mock.pods.delete.assert_called_once_with(pod_id)

    def test_do_pod_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        pod_id = 'id'
        args.pod = pod_id

        shell.do_pod_show(client_mock, args)
        client_mock.pods.get.assert_called_once_with(pod_id)

    def test_do_rc_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        shell.do_rc_list(client_mock, args)
        client_mock.rcs.list.assert_called_once_with()

    def test_do_rc_create(self):
        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = 'CREATE_COMPLETE'
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        manifest_url = "test_url"
        args.manifest_url = manifest_url
        bay_id_or_name = "xxx"
        args.bay_id = bay_id_or_name
        manifest = "test_manifest"
        args.manifest = manifest

        shell.do_rc_create(client_mock, args)
        client_mock.rcs.create.assert_called_once_with(
            manifest_url=manifest_url, bay_uuid=bay.uuid)

    def test_do_rc_create_with_bay_status_wrong(self):
        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = 'XXX'
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        manifest_url = "test_url"
        args.manifest_url = manifest_url
        bay_id_or_name = "xxx"
        args.bay_id = bay_id_or_name
        manifest = "test_manifest"
        args.manifest = manifest

        shell.do_rc_create(client_mock, args)
        self.assertFalse(client_mock.rcs.create.called)

    def test_do_rc_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        rc_id = 'id'
        args.rc = rc_id
        op = 'replace'
        args.op = op
        attributes = 'manifest={}'
        args.attributes = attributes
        shell.magnum_utils.args_array_to_patch = mock.MagicMock()
        patch = [{'path': '/manifest', 'value': '{}', 'op': 'replace'}]
        shell.magnum_utils.args_array_to_patch.return_value = patch

        shell.do_rc_update(client_mock, args)
        client_mock.rcs.update.assert_called_once_with(rc_id, patch)

    def test_do_rc_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        rc_id = 'id'
        args.rcs = [rc_id]

        shell.do_rc_delete(client_mock, args)
        client_mock.rcs.delete.assert_called_once_with(rc_id)

    def test_do_rc_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        rc_id = 'id'
        args.rc = rc_id

        shell.do_rc_show(client_mock, args)
        client_mock.rcs.get.assert_called_once_with(rc_id)

    def test_do_coe_service_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        shell.do_coe_service_list(client_mock, args)
        client_mock.services.list.assert_called_once_with()

    def test_do_coe_service_create(self):
        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = "CREATE_COMPLETE"
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        manifest_url = "test_url"
        args.manifest_url = manifest_url
        bay_id_or_name = "xxx"
        args.bay_id = bay_id_or_name
        manifest = "test_manifest"
        args.manifest = manifest

        shell.do_coe_service_create(client_mock, args)
        client_mock.services.create.assert_called_once_with(
            manifest_url=manifest_url, bay_uuid=bay.uuid)

    def test_do_service_create_with_bay_status_wrong(self):
        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = "XXX"
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        manifest_url = "test_url"
        args.manifest_url = manifest_url
        bay_id_or_name = "xxx"
        args.bay_id = bay_id_or_name
        manifest = "test_manifest"
        args.manifest = manifest

        shell.do_coe_service_create(client_mock, args)
        self.assertFalse(client_mock.services.create.called)

    def test_do_coe_service_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        service_id = 'id'
        args.service = service_id
        op = 'replace'
        args.op = op
        attributes = 'manifest={}'
        args.attributes = attributes
        shell.magnum_utils.args_array_to_patch = mock.MagicMock()
        patch = [{'path': '/manifest', 'value': '{}', 'op': 'replace'}]
        shell.magnum_utils.args_array_to_patch.return_value = patch

        shell.do_coe_service_update(client_mock, args)
        client_mock.services.update.assert_called_once_with(service_id, patch)

    def test_do_coe_service_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        service_id = 'id'
        args.services = [service_id]

        shell.do_coe_service_delete(client_mock, args)
        client_mock.services.delete.assert_called_once_with(service_id)

    def test_do_coe_service_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        service_id = 'id'
        args.service = service_id

        shell.do_coe_service_show(client_mock, args)
        client_mock.services.get.assert_called_once_with(service_id)

    def test_do_container_create(self):
        client_mock = mock.MagicMock()
        bay = mock.MagicMock()
        bay.uuid = 'uuid'
        bay.status = "CREATE_COMPLETE"
        client_mock.bays.get.return_value = bay

        args = mock.MagicMock()
        name = "containe1"
        args.name = name
        image = "test_image"
        args.image = image
        bay_id_or_name = "xxx"
        args.bay_id = bay_id_or_name
        command = "test_command"
        args.command = command

        shell.do_container_create(client_mock, args)
        client_mock.containers.create.assert_called_once_with(
            name=name, image=image, bay_uuid=bay.uuid, command=command)

    def test_do_container_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        shell.do_container_list(client_mock, args)
        client_mock.containers.list.assert_called_once_with()

    def test_do_container_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = "container_id"
        args.containers = [container_id]

        shell.do_container_delete(client_mock, args)
        client_mock.containers.delete.assert_called_once_with(container_id)

    def test_do_container_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = "container_id"
        args.container = container_id
        args.json = None

        shell.do_container_show(client_mock, args)
        client_mock.containers.get.assert_called_once_with(container_id)

    def test_do_container_reboot(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.containers = [container_id]

        shell.do_container_reboot(client_mock, args)
        client_mock.containers.reboot.assert_called_once_with(container_id)

    def test_do_container_stop(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.containers = [container_id]

        shell.do_container_stop(client_mock, args)
        client_mock.containers.stop.assert_called_once_with(container_id)

    def test_do_container_start(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.containers = [container_id]

        shell.do_container_start(client_mock, args)
        client_mock.containers.start.assert_called_once_with(container_id)

    def test_do_container_pause(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.containers = [container_id]

        shell.do_container_pause(client_mock, args)
        client_mock.containers.pause.assert_called_once_with(container_id)

    def test_do_container_unpause(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.containers = [container_id]

        shell.do_container_unpause(client_mock, args)
        client_mock.containers.unpause.assert_called_once_with(container_id)

    def test_do_container_logs(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.container = container_id

        shell.do_container_logs(client_mock, args)
        client_mock.containers.logs.assert_called_once_with(container_id)

    def test_do_container_exec(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.container = container_id
        command = 'ls'
        args.command = command

        shell.do_container_exec(client_mock, args)
        client_mock.containers.execute.assert_called_once_with(
            container_id, command)
