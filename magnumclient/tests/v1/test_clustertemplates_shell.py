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

import mock

from magnumclient.common.apiclient import exceptions
from magnumclient.tests.v1 import shell_test_base
from magnumclient.v1.cluster_templates import ClusterTemplate


class FakeClusterTemplate(ClusterTemplate):
    def __init__(self, manager=None, info={}, **kwargs):
        ClusterTemplate.__init__(self, manager=manager, info=info)
        self.apiserver_port = kwargs.get('apiserver_port', None)
        self.uuid = kwargs.get('uuid', 'x')
        self.links = kwargs.get('links', [])
        self.server_type = kwargs.get('server_type', 'vm')
        self.image_id = kwargs.get('image', 'x')
        self.tls_disabled = kwargs.get('tls_disabled', False)
        self.registry_enabled = kwargs.get('registry_enabled', False)
        self.coe = kwargs.get('coe', 'x')
        self.public = kwargs.get('public', False)
        self.name = kwargs.get('name', 'x')


class ShellTest(shell_test_base.TestCommandLineArgument):

    def _get_expected_args_list(self, limit=None, sort_dir=None,
                                sort_key=None, detail=False):
        expected_args = {}
        expected_args['limit'] = limit
        expected_args['sort_dir'] = sort_dir
        expected_args['sort_key'] = sort_key
        expected_args['detail'] = detail

        return expected_args

    def _get_expected_args(self, image_id, external_network_id, coe,
                           master_flavor_id=None, name=None,
                           keypair_id=None, fixed_network=None,
                           fixed_subnet=None, network_driver=None,
                           volume_driver=None, dns_nameserver='8.8.8.8',
                           flavor_id='m1.medium',
                           docker_storage_driver='devicemapper',
                           docker_volume_size=None, http_proxy=None,
                           https_proxy=None, no_proxy=None, labels={},
                           tls_disabled=False, public=False,
                           master_lb_enabled=False, server_type='vm',
                           floating_ip_enabled=True,
                           registry_enabled=False,
                           insecure_registry=None):

        expected_args = {}
        expected_args['image_id'] = image_id
        expected_args['external_network_id'] = external_network_id
        expected_args['coe'] = coe
        expected_args['master_flavor_id'] = master_flavor_id
        expected_args['name'] = name
        expected_args['keypair_id'] = keypair_id
        expected_args['fixed_network'] = fixed_network
        expected_args['fixed_subnet'] = fixed_subnet
        expected_args['network_driver'] = network_driver
        expected_args['volume_driver'] = volume_driver
        expected_args['dns_nameserver'] = dns_nameserver
        expected_args['flavor_id'] = flavor_id
        expected_args['docker_volume_size'] = docker_volume_size
        expected_args['docker_storage_driver'] = docker_storage_driver
        expected_args['http_proxy'] = http_proxy
        expected_args['https_proxy'] = https_proxy
        expected_args['no_proxy'] = no_proxy
        expected_args['labels'] = labels
        expected_args['tls_disabled'] = tls_disabled
        expected_args['public'] = public
        expected_args['master_lb_enabled'] = master_lb_enabled
        expected_args['server_type'] = server_type
        expected_args['floating_ip_enabled'] = floating_ip_enabled
        expected_args['registry_enabled'] = registry_enabled
        expected_args['insecure_registry'] = insecure_registry

        return expected_args

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_success(self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test '
                               '--image-id test_image '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--coe swarm '
                               '--dns-nameserver test_dns '
                               '--flavor-id test_flavor '
                               '--fixed-network private '
                               '--fixed-subnet private-subnet '
                               '--volume-driver test_volume '
                               '--network-driver test_driver '
                               '--labels key=val '
                               '--master-flavor-id test_flavor '
                               '--docker-volume-size 10 '
                               '--docker-storage-driver devicemapper '
                               '--public '
                               '--server-type vm '
                               '--master-lb-enabled '
                               '--floating-ip-enabled ')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    dns_nameserver='test_dns', public=True,
                                    flavor_id='test_flavor',
                                    master_flavor_id='test_flavor',
                                    fixed_network='private',
                                    fixed_subnet='private-subnet',
                                    server_type='vm',
                                    network_driver='test_driver',
                                    volume_driver='test_volume',
                                    docker_storage_driver='devicemapper',
                                    docker_volume_size=10,
                                    master_lb_enabled=True,
                                    floating_ip_enabled=True,
                                    labels={'key': 'val'})
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('cluster-template-create '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe kubernetes '
                               '--name test '
                               '--server-type vm')

        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair',
                                    coe='kubernetes',
                                    external_network_id='test_net',
                                    server_type='vm')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_success_no_servertype(self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test '
                               '--image-id test_image '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--coe swarm '
                               '--dns-nameserver test_dns '
                               '--flavor-id test_flavor '
                               '--fixed-network public '
                               '--network-driver test_driver '
                               '--labels key=val '
                               '--master-flavor-id test_flavor '
                               '--docker-volume-size 10 '
                               '--docker-storage-driver devicemapper '
                               '--public ')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    dns_nameserver='test_dns', public=True,
                                    flavor_id='test_flavor',
                                    master_flavor_id='test_flavor',
                                    fixed_network='public',
                                    network_driver='test_driver',
                                    docker_storage_driver='devicemapper',
                                    docker_volume_size=10,
                                    labels={'key': 'val'})
        mock_create.assert_called_with(**expected_args)

        self._test_arg_success('cluster-template-create '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe kubernetes '
                               '--name test ')

        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair',
                                    coe='kubernetes',
                                    external_network_id='test_net')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_success_with_registry_enabled(
        self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test '
                               '--network-driver test_driver '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--registry-enabled')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    network_driver='test_driver',
                                    registry_enabled=True)
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_public_success(self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test --network-driver test_driver '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--public '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    public=True, server_type='vm',
                                    network_driver='test_driver')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_success_with_master_flavor(self,
                                                                mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test '
                               '--image-id test_image '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--coe swarm '
                               '--dns-nameserver test_dns '
                               '--master-flavor-id test_flavor')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    dns_nameserver='test_dns',
                                    master_flavor_id='test_flavor')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_docker_vol_size_success(self,
                                                             mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test --docker-volume-size 4514 '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    server_type='vm',
                                    docker_volume_size=4514)
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_docker_storage_driver_success(
            self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--docker-storage-driver devicemapper '
                               '--coe swarm'
                               )
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    docker_storage_driver='devicemapper')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_fixed_network_success(self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test --fixed-network private '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    fixed_network='private',
                                    external_network_id='test_net',
                                    server_type='vm')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_network_driver_success(self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test --network-driver test_driver '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    server_type='vm',
                                    network_driver='test_driver')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_volume_driver_success(self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test --volume-driver test_volume '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    server_type='vm',
                                    volume_driver='test_volume')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_http_proxy_success(self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test --fixed-network private '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--http-proxy http_proxy '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    fixed_network='private',
                                    server_type='vm',
                                    http_proxy='http_proxy')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_https_proxy_success(self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test --fixed-network private '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--https-proxy https_proxy '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    fixed_network='private',
                                    server_type='vm',
                                    https_proxy='https_proxy')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_no_proxy_success(self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test --fixed-network private '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--no-proxy no_proxy '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    fixed_network='private',
                                    server_type='vm',
                                    no_proxy='no_proxy')
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_labels_success(self, mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test '
                               '--labels key=val '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    server_type='vm',
                                    labels={'key': 'val'})
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_separate_labels_success(self,
                                                             mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test '
                               '--labels key1=val1 '
                               '--labels key2=val2 '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    server_type='vm',
                                    labels={'key1': 'val1', 'key2': 'val2'})
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_combined_labels_success(self,
                                                             mock_create):
        self._test_arg_success('cluster-template-create '
                               '--name test '
                               '--labels key1=val1,key2=val2 '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    server_type='vm',
                                    labels={'key1': 'val1', 'key2': 'val2'})
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_success_only_positional_name(self,
                                                                  mock_create):
        self._test_arg_success('cluster-template-create '
                               'test '
                               '--labels key1=val1,key2=val2 '
                               '--keypair-id test_keypair '
                               '--external-network-id test_net '
                               '--image-id test_image '
                               '--coe swarm '
                               '--server-type vm')
        expected_args = \
            self._get_expected_args(name='test', image_id='test_image',
                                    keypair_id='test_keypair', coe='swarm',
                                    external_network_id='test_net',
                                    server_type='vm',
                                    labels={'key1': 'val1', 'key2': 'val2'})
        mock_create.assert_called_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_failure_duplicate_name(self, mock_create):
        self._test_arg_failure('cluster-template-create '
                               'foo --name test', self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_failure_few_arg(self, mock_create):
        self._test_arg_failure('cluster-template-create '
                               '--name test', self._mandatory_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure('cluster-template-create '
                               '--image-id test', self._mandatory_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure('cluster-template-create '
                               '--keypair-id test', self._mandatory_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure('cluster-template-create '
                               '--external-network-id test',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure('cluster-template-create '
                               '--coe test',
                               self._mandatory_group_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure('cluster-template-create '
                               '--coe test '
                               '--external-network test ',
                               self._mandatory_group_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure('cluster-template-create '
                               '--coe test '
                               '--image test ',
                               self._mandatory_group_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure('cluster-template-create '
                               '--server-type test', self._mandatory_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure('cluster-template-create',
                               self._mandatory_arg_error)
        mock_create.assert_not_called()

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_deprecation_errors(self, mock_create):
        required_args = ('cluster-template-create '
                         '--coe test --external-network public --image test ')
        self._test_arg_failure('cluster-template-create --coe test '
                               '--external-network-id test '
                               '--external-network test ',
                               self._too_many_group_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure('cluster-template-create --coe test '
                               '--image-id test '
                               '--image test ',
                               self._too_many_group_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure(required_args +
                               '--flavor test --flavor-id test',
                               self._too_many_group_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure(required_args +
                               '--master-flavor test --master-flavor-id test',
                               self._too_many_group_arg_error)
        mock_create.assert_not_called()

        self._test_arg_failure(required_args +
                               '--keypair test --keypair-id test',
                               self._too_many_group_arg_error)
        mock_create.assert_not_called()

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.create')
    def test_cluster_template_create_deprecation_warnings(self, mock_create):
        required_args = ('cluster-template-create '
                         '--coe test --external-network public --image test ')
        self._test_arg_failure('cluster-template-create '
                               '--coe test '
                               '--external-network-id test '
                               '--image test ',
                               self._deprecated_warning)
        expected_args = \
            self._get_expected_args(image_id='test', coe='test',
                                    external_network_id='test')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_failure('cluster-template-create '
                               '--coe test '
                               '--external-network test '
                               '--image-id test ',
                               self._deprecated_warning)
        expected_args = \
            self._get_expected_args(image_id='test', coe='test',
                                    external_network_id='test')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_failure('cluster-template-create '
                               '--coe test '
                               '--external-network-id test '
                               '--image-id test ',
                               self._deprecated_warning)
        expected_args = \
            self._get_expected_args(image_id='test', coe='test',
                                    external_network_id='test')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_failure(required_args + '--keypair-id test',
                               self._deprecated_warning)
        expected_args = \
            self._get_expected_args(image_id='test', coe='test',
                                    keypair_id='test',
                                    external_network_id='public')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_failure(required_args + '--flavor-id test',
                               self._deprecated_warning)
        expected_args = \
            self._get_expected_args(image_id='test', coe='test',
                                    flavor_id='test',
                                    external_network_id='public')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_failure(required_args + '--master-flavor-id test',
                               self._deprecated_warning)
        expected_args = \
            self._get_expected_args(image_id='test', coe='test',
                                    master_flavor_id='test',
                                    external_network_id='public')
        mock_create.assert_called_with(**expected_args)

        self._test_arg_failure(required_args + '--name foo',
                               self._deprecated_warning)
        expected_args = \
            self._get_expected_args(image_id='test', coe='test',
                                    name='foo',
                                    external_network_id='public')
        mock_create.assert_called_with(**expected_args)

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    def test_cluster_template_show_success(self, mock_show):
        self._test_arg_success('cluster-template-show xxx')
        mock_show.assert_called_once_with('xxx')

    @mock.patch('magnumclient.v1.cluster_templates.ClusterTemplateManager.get')
    def test_cluster_template_show_failure_no_arg(self, mock_show):
        self._test_arg_failure('cluster-template-show',
                               self._few_argument_error)
        mock_show.assert_not_called()

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.delete')
    def test_cluster_template_delete_success(self, mock_delete):
        self._test_arg_success('cluster-template-delete xxx')
        mock_delete.assert_called_once_with('xxx')

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.delete')
    def test_cluster_template_delete_multiple_id_success(self, mock_delete):
        self._test_arg_success('cluster-template-delete xxx xyz')
        calls = [mock.call('xxx'), mock.call('xyz')]
        mock_delete.assert_has_calls(calls)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.delete')
    def test_cluster_template_delete_failure_no_arg(self, mock_delete):
        self._test_arg_failure('cluster-template-delete',
                               self._few_argument_error)
        mock_delete.assert_not_called()

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.update')
    def test_cluster_template_update_success(self, mock_update):
        self._test_arg_success('cluster-template-update test add test=test')
        patch = [{'op': 'add', 'path': '/test', 'value': 'test'}]
        mock_update.assert_called_once_with('test', patch)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.update')
    def test_cluster_template_update_success_many_attribute(self, mock_update):
        self._test_arg_success('cluster-template-update test '
                               'add test=test test1=test1')
        patch = [{'op': 'add', 'path': '/test', 'value': 'test'},
                 {'op': 'add', 'path': '/test1', 'value': 'test1'}]
        mock_update.assert_called_once_with('test', patch)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.update')
    def test_cluster_template_update_failure_wrong_op(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum cluster-template-update ',
            '.*?^error: argument <op>: invalid choice: ',
            ".*?^Try 'magnum help cluster-template-update' "
            "for more information."
            ]
        self._test_arg_failure('cluster-template-update test wrong test=test',
                               _error_msg)
        mock_update.assert_not_called()

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.update')
    def test_cluster_template_update_failure_few_args(self, mock_update):
        _error_msg = [
            '.*?^usage: magnum cluster-template-update ',
            '.*?^error: (the following arguments|too few arguments)',
            ".*?^Try 'magnum help cluster-template-update' "
            "for more information."
            ]
        self._test_arg_failure('cluster-template-update', _error_msg)
        mock_update.assert_not_called()

        self._test_arg_failure('cluster-template-update test', _error_msg)
        mock_update.assert_not_called()

        self._test_arg_failure('cluster-template-update test add', _error_msg)
        mock_update.assert_not_called()

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.list')
    def test_cluster_template_list_success(self, mock_list):
        self._test_arg_success('cluster-template-list')
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.list')
    def test_cluster_template_list_success_with_arg(self, mock_list):
        self._test_arg_success('cluster-template-list '
                               '--limit 1 '
                               '--sort-dir asc '
                               '--sort-key uuid')
        expected_args = self._get_expected_args_list(1, 'asc', 'uuid')
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.list')
    def test_cluster_template_list_success_detailed(self, mock_list):
        self._test_arg_success('cluster-template-list '
                               '--detail')
        expected_args = self._get_expected_args_list(detail=True)
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.list')
    def test_cluster_template_list_ignored_duplicated_field(self, mock_list):
        mock_list.return_value = [FakeClusterTemplate()]
        self._test_arg_success(
            'cluster-template-list --fields coe,coe,coe,name,name',
            keyword='\n| uuid | name | Coe |\n')
        # Output should be
        # +------+------+-----+
        # | uuid | name | Coe |
        # +------+------+-----+
        # | x    | x    | x   |
        # +------+------+-----+
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.list')
    def test_cluster_template_list_failure_with_invalid_field(self, mock_list):
        mock_list.return_value = [FakeClusterTemplate()]
        _error_msg = [".*?^Non-existent fields are specified: ['xxx','zzz']"]
        self.assertRaises(exceptions.CommandError,
                          self._test_arg_failure,
                          'cluster-template-list --fields xxx,coe,zzz',
                          _error_msg)
        expected_args = self._get_expected_args_list()
        mock_list.assert_called_once_with(**expected_args)

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.list')
    def test_cluster_template_list_failure_invalid_arg(self, mock_list):
        _error_msg = [
            '.*?^usage: magnum cluster-template-list ',
            '.*?^error: argument --sort-dir: invalid choice: ',
            ".*?^Try 'magnum help cluster-template-list' for more information."
            ]
        self._test_arg_failure('cluster-template-list --sort-dir aaa',
                               _error_msg)
        mock_list.assert_not_called()

    @mock.patch(
        'magnumclient.v1.cluster_templates.ClusterTemplateManager.list')
    def test_cluster_template_list_failure(self, mock_list):
        self._test_arg_failure('cluster-template-list --wrong',
                               self._unrecognized_arg_error)
        mock_list.assert_not_called()
