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

import json

import mock

from magnumclient.tests import base
from magnumclient.v1 import shell


container_fixture = {
    "name": "container",
    "image_id": "image_id"
}


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
        args = mock.MagicMock()
        node_count = 1
        args.node_count = node_count
        name = "test_bay"
        args.name = name
        baymodel_id = "test_baymodel_id"
        args.baymodel_id = baymodel_id

        shell.do_bay_create(client_mock, args)
        client_mock.bays.create.assert_called_once_with(
            name=name, node_count=node_count, baymodel_id=baymodel_id)

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
        ssh_authorized_key = "test_key"
        args.ssh_authorized_key = ssh_authorized_key

        shell.do_baymodel_create(client_mock, args)
        client_mock.baymodels.create.assert_called_once_with(
            name=name, image_id=image_id, flavor_id=flavor_id,
            master_flavor_id=master_flavor_id, keypair_id=keypair_id,
            external_network_id=external_network_id,
            docker_volume_size=docker_volume_size,
            fixed_network=fixed_network, dns_nameserver=dns_nameserver,
            ssh_authorized_key=ssh_authorized_key)

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
        args = mock.MagicMock()
        manifest_url = "test_url"
        args.manifest_url = manifest_url
        bay_id = "xxx"
        args.bay_id = bay_id
        manifest = "test_manifest"
        args.manifest = manifest

        shell.do_rc_create(client_mock, args)
        client_mock.rcs.create.assert_called_once_with(
            manifest_url=manifest_url, bay_uuid=bay_id)

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

    def test_do_service_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        shell.do_service_list(client_mock, args)
        client_mock.services.list.assert_called_once_with()

    def test_do_service_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        manifest_url = "test_url"
        args.manifest_url = manifest_url
        bay_id = "xxx"
        args.bay_id = bay_id
        manifest = "test_manifest"
        args.manifest = manifest

        shell.do_service_create(client_mock, args)
        client_mock.services.create.assert_called_once_with(
            manifest_url=manifest_url, bay_uuid=bay_id)

    def test_do_service_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        service_id = 'id'
        args.services = [service_id]

        shell.do_service_delete(client_mock, args)
        client_mock.services.delete.assert_called_once_with(service_id)

    def test_do_service_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        service_id = 'id'
        args.service = service_id

        shell.do_service_show(client_mock, args)
        client_mock.services.get.assert_called_once_with(service_id)

    def test_do_container_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.json.read.return_value = json.dumps(container_fixture)

        shell.do_container_create(client_mock, args)
        client_mock.containers.create.assert_called_once_with(
            **container_fixture)

    def test_do_container_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        shell.do_container_list(client_mock, args)
        client_mock.containers.list.assert_called_once_with()

    def test_do_container_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = "container_id"
        args.id = [container_id]

        shell.do_container_delete(client_mock, args)
        client_mock.containers.delete.assert_called_once_with(container_id)

    def test_do_container_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = "container_id"
        args.id = container_id
        args.json = None

        shell.do_container_show(client_mock, args)
        client_mock.containers.get.assert_called_once_with(container_id)

    def test_do_container_reboot(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.id = [container_id]

        shell.do_container_reboot(client_mock, args)
        client_mock.containers.reboot.assert_called_once_with(container_id)

    def test_do_container_stop(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.id = [container_id]

        shell.do_container_stop(client_mock, args)
        client_mock.containers.stop.assert_called_once_with(container_id)

    def test_do_container_start(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.id = [container_id]

        shell.do_container_start(client_mock, args)
        client_mock.containers.start.assert_called_once_with(container_id)

    def test_do_container_pause(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.id = [container_id]

        shell.do_container_pause(client_mock, args)
        client_mock.containers.pause.assert_called_once_with(container_id)

    def test_do_container_unpause(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.id = [container_id]

        shell.do_container_unpause(client_mock, args)
        client_mock.containers.unpause.assert_called_once_with(container_id)

    def test_do_container_logs(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.id = container_id

        shell.do_container_logs(client_mock, args)
        client_mock.containers.logs.assert_called_once_with(container_id)

    def test_do_container_execute(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = 'id'
        args.id = container_id
        command = 'ls'
        args.command = command

        shell.do_container_execute(client_mock, args)
        client_mock.containers.execute.assert_called_once_with(
            container_id, command)
