# Copyright 2016 EasyStack.  All rights reserved.
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

from magnumclient.common import utils as magnum_utils
from magnumclient.exceptions import InvalidAttribute
from magnumclient.i18n import _

from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging


CLUSTER_TEMPLATE_ATTRIBUTES = [
    'insecure_registry',
    'labels',
    'updated_at',
    'floating_ip_enabled',
    'fixed_subnet',
    'master_flavor_id',
    'uuid',
    'no_proxy',
    'https_proxy',
    'tls_disabled',
    'keypair_id',
    'public',
    'http_proxy',
    'docker_volume_size',
    'server_type',
    'external_network_id',
    'cluster_distro',
    'image_id',
    'volume_driver',
    'registry_enabled',
    'docker_storage_driver',
    'apiserver_port',
    'name',
    'created_at',
    'network_driver',
    'fixed_network',
    'coe',
    'flavor_id',
    'master_lb_enabled',
    'dns_nameserver',
    'hidden'
]


def _show_cluster_template(cluster_template):
    del cluster_template._info['links']
    for field in cluster_template._info:
        if cluster_template._info[field] is None:
            setattr(cluster_template, field, '-')
    columns = CLUSTER_TEMPLATE_ATTRIBUTES
    return columns, osc_utils.get_item_properties(cluster_template, columns)


class CreateClusterTemplate(command.ShowOne):
    """Create a Cluster Template."""
    _description = _("Create a Cluster Template.")

    def get_parser(self, prog_name):
        parser = super(CreateClusterTemplate, self).get_parser(prog_name)

        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the cluster template to create.'))
        parser.add_argument(
            '--coe',
            required=True,
            metavar='<coe>',
            help=_('Specify the Container Orchestration Engine to use.'))
        parser.add_argument(
            '--image',
            required=True,
            metavar='<image>',
            help=_('The name or UUID of the base image to customize for the '
                   'Cluster.'))
        parser.add_argument(
            '--external-network',
            dest='external_network',
            required=True,
            metavar='<external-network>',
            help=_('The external Neutron network name or UUID to connect to '
                   'this Cluster Template.'))
        parser.add_argument(
            '--keypair',
            metavar='<keypair>',
            help=_('The name or UUID of the SSH keypair to load into the '
                   'Cluster nodes.'))
        parser.add_argument(
            '--fixed-network',
            dest='fixed_network',
            metavar='<fixed-network>',
            help=_('The private Neutron network name to connect to this '
                   'Cluster model.'))
        parser.add_argument(
            '--fixed-subnet',
            dest='fixed_subnet',
            metavar='<fixed-subnet>',
            help=_('The private Neutron subnet name to connect to Cluster.'))
        parser.add_argument(
            '--network-driver',
            dest='network_driver',
            metavar='<network-driver>',
            help=_('The network driver name for instantiating container '
                   'networks.'))
        parser.add_argument(
            '--volume-driver',
            dest='volume_driver',
            metavar='<volume-driver>',
            help=_('The volume driver name for instantiating container '
                   'volume.'))
        parser.add_argument(
            '--dns-nameserver',
            dest='dns_nameserver',
            metavar='<dns-nameserver>',
            default='8.8.8.8',
            help=_('The DNS nameserver to use for this cluster template.'))
        parser.add_argument(
            '--flavor',
            metavar='<flavor>',
            default='m1.medium',
            help=_('The nova flavor name or UUID to use when launching the '
                   'Cluster.'))
        parser.add_argument(
            '--master-flavor',
            dest='master_flavor',
            metavar='<master-flavor>',
            help=_('The nova flavor name or UUID to use when launching the '
                   'master node of the Cluster.'))
        parser.add_argument(
            '--docker-volume-size',
            dest='docker_volume_size',
            metavar='<docker-volume-size>',
            type=int,
            help=_('Specify the number of size in GB for the docker volume '
                   'to use.'))
        parser.add_argument(
            '--docker-storage-driver',
            dest='docker_storage_driver',
            metavar='<docker-storage-driver>',
            default='devicemapper',
            help=_('Select a docker storage driver. Supported: devicemapper, '
                   'overlay. Default: devicemapper'))
        parser.add_argument(
            '--http-proxy',
            dest='http_proxy',
            metavar='<http-proxy>',
            help=_('The http_proxy address to use for nodes in Cluster.'))
        parser.add_argument(
            '--https-proxy',
            dest='https_proxy',
            metavar='<https-proxy>',
            help=_('The https_proxy address to use for nodes in Cluster.'))
        parser.add_argument(
            '--no-proxy',
            dest='no_proxy',
            metavar='<no-proxy>',
            help=_('The no_proxy address to use for nodes in Cluster.'))
        parser.add_argument(
            '--labels',
            metavar='<KEY1=VALUE1,KEY2=VALUE2;KEY3=VALUE3...>',
            action='append',
            default=[],
            help=_('Arbitrary labels in the form of key=value pairs to '
                   'associate with a cluster template. May be used multiple '
                   'times.'))
        parser.add_argument(
            '--tls-disabled',
            dest='tls_disabled',
            action='store_true',
            default=False,
            help=_('Disable TLS in the Cluster.'))
        parser.add_argument(
            '--public',
            action='store_true',
            default=False,
            help=_('Make cluster template public.'))
        parser.add_argument(
            '--registry-enabled',
            dest='registry_enabled',
            action='store_true',
            default=False,
            help=_('Enable docker registry in the Cluster'))
        parser.add_argument(
            '--server-type',
            dest='server_type',
            metavar='<server-type>',
            default='vm',
            help=_('Specify the server type to be used for example vm. '
                   'For this release default server type will be vm.'))
        parser.add_argument(
            '--master-lb-enabled',
            dest='master_lb_enabled',
            action='store_true',
            default=False,
            help=_('Indicates whether created Clusters should have a load '
                   'balancer for master nodes or not.'))
        parser.add_argument(
            '--floating-ip-enabled',
            dest='floating_ip_enabled',
            default=[],
            action='append_const',
            const=True,
            help=_('Indicates whether created Clusters should have a '
                   'floating ip.'))
        parser.add_argument(
            '--floating-ip-disabled',
            dest='floating_ip_enabled',
            action='append_const',
            const=False,
            help=_('Disables floating ip creation on the new Cluster'))
        parser.add_argument(
            '--hidden',
            dest='hidden',
            action='store_true',
            default=False,
            help=_('Indicates the cluster template should be hidden.'))
        parser.add_argument(
            '--visible',
            dest='hidden',
            action='store_false',
            help=_('Indicates the cluster template should be visible.'))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        mag_client = self.app.client_manager.container_infra
        args = {
            'name': parsed_args.name,
            'image_id': parsed_args.image,
            'keypair_id': parsed_args.keypair,
            'external_network_id': parsed_args.external_network,
            'coe': parsed_args.coe,
            'fixed_network': parsed_args.fixed_network,
            'fixed_subnet': parsed_args.fixed_subnet,
            'network_driver': parsed_args.network_driver,
            'volume_driver': parsed_args.volume_driver,
            'dns_nameserver': parsed_args.dns_nameserver,
            'flavor_id': parsed_args.flavor,
            'master_flavor_id': parsed_args.master_flavor,
            'docker_volume_size': parsed_args.docker_volume_size,
            'docker_storage_driver': parsed_args.docker_storage_driver,
            'http_proxy': parsed_args.http_proxy,
            'https_proxy': parsed_args.https_proxy,
            'no_proxy': parsed_args.no_proxy,
            'labels': magnum_utils.handle_labels(parsed_args.labels),
            'tls_disabled': parsed_args.tls_disabled,
            'public': parsed_args.public,
            'registry_enabled': parsed_args.registry_enabled,
            'server_type': parsed_args.server_type,
            'master_lb_enabled': parsed_args.master_lb_enabled,
        }

        # NOTE (brtknr): Only supply hidden arg if it is True
        # for backward compatibility
        if parsed_args.hidden:
            args['hidden'] = parsed_args.hidden

        if len(parsed_args.floating_ip_enabled) > 1:
            raise InvalidAttribute('--floating-ip-enabled and '
                                   '--floating-ip-disabled are '
                                   'mutually exclusive and '
                                   'should be specified only once.')
        elif len(parsed_args.floating_ip_enabled) == 1:
            args['floating_ip_enabled'] = parsed_args.floating_ip_enabled[0]

        ct = mag_client.cluster_templates.create(**args)
        print("Request to create cluster template %s accepted"
              % parsed_args.name)
        return _show_cluster_template(ct)


class DeleteClusterTemplate(command.Command):
    """Delete a Cluster Template."""
    _description = _("Delete a Cluster Template.")

    def get_parser(self, prog_name):
        parser = super(DeleteClusterTemplate, self).get_parser(prog_name)
        parser.add_argument(
            'cluster-templates',
            metavar='<cluster-templates>',
            nargs='+',
            help=_('ID or name of the (cluster template)s to delete.'))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra

        for cluster_template in getattr(parsed_args, 'cluster-templates'):
            try:
                mag_client.cluster_templates.delete(cluster_template)
                print(
                    "Request to delete cluster template %s has been accepted."
                    % cluster_template)
            except Exception as e:
                print("Delete for cluster template "
                      "%(cluster_template)s failed: %(e)s" %
                      {'cluster_template': cluster_template, 'e': e})


class ListTemplateCluster(command.Lister):
    """List Cluster Templates."""
    _description = _("List Cluster Templates.")

    log = logging.getLogger(__name__ + ".ListTemplateCluster")

    def get_parser(self, prog_name):
        parser = super(ListTemplateCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of cluster templates to return'))
        parser.add_argument(
            '--sort-key',
            metavar='<sort-key>',
            help=_('Column to sort results by'))
        parser.add_argument(
            '--sort-dir',
            metavar='<sort-dir>',
            choices=['desc', 'asc'],
            help=_('Direction to sort. "asc" or "desc".'))
        parser.add_argument(
            '--fields',
            default=None,
            metavar='<fields>',
            help=_('Comma-separated list of fields to display. '
                   'Available fields: uuid, name, coe, image_id, public, '
                   'link, apiserver_port, server_type, tls_disabled, '
                   'registry_enabled'
                   )
            )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        columns = ['uuid', 'name']
        cts = mag_client.cluster_templates.list(limit=parsed_args.limit,
                                                sort_key=parsed_args.sort_key,
                                                sort_dir=parsed_args.sort_dir)
        return (
            columns,
            (osc_utils.get_item_properties(ct, columns) for ct in cts)
        )


class ShowClusterTemplate(command.ShowOne):
    """Show a Cluster Template."""
    _description = _("Show a Cluster Template.")

    log = logging.getLogger(__name__ + ".ShowClusterTemplate")

    def get_parser(self, prog_name):
        parser = super(ShowClusterTemplate, self).get_parser(prog_name)
        parser.add_argument(
            'cluster-template',
            metavar='<cluster-template>',
            help=_('ID or name of the cluster template to show.'))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        ct = getattr(parsed_args, 'cluster-template', None)
        cluster_template = mag_client.cluster_templates.get(ct)

        return _show_cluster_template(cluster_template)


class UpdateClusterTemplate(command.ShowOne):
    """Update a Cluster Template."""

    log = logging.getLogger(__name__ + ".UpdateClusterTemplate")

    def get_parser(self, prog_name):
        parser = super(UpdateClusterTemplate, self).get_parser(prog_name)
        parser.add_argument(
            'cluster-template',
            metavar='<cluster-template>',
            help=_('The name or UUID of cluster template to update'))

        parser.add_argument(
            'op',
            metavar='<op>',
            choices=['add', 'replace', 'remove'],
            help=_("Operations: one of 'add', 'replace' or 'remove'"))

        parser.add_argument(
            'attributes',
            metavar='<path=value>',
            nargs='+',
            action='append',
            default=[],
            help=_(
                "Attributes to add/replace or remove (only PATH is necessary "
                "on remove)"))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        patch = magnum_utils.args_array_to_patch(parsed_args.op,
                                                 parsed_args.attributes[0])
        name = getattr(parsed_args, 'cluster-template', None)
        ct = mag_client.cluster_templates.update(name, patch)
        return _show_cluster_template(ct)
