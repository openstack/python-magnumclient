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

from magnumclient.common import cliutils as utils
from magnumclient.common import utils as magnum_utils
from magnumclient.i18n import _
from magnumclient.v1 import basemodels


# Maps old parameter names to their new names and whether they are required
DEPRECATING_PARAMS = {
    "--external-network-id": "--external-network",
    "--flavor-id": "--flavor",
    "--image-id": "--image",
    "--keypair-id": "--keypair",
    "--master-flavor-id": "--master-flavor",
}


def _show_cluster_template(cluster_template):
    del cluster_template._info['links']
    utils.print_dict(cluster_template._info)


@utils.deprecation_map(DEPRECATING_PARAMS)
@utils.arg('positional_name',
           metavar='<name>',
           nargs='?',
           default=None,
           help=_('Name of the cluster template to create.'))
@utils.arg('--name',
           metavar='<name>',
           default=None,
           help=(_('Name of the cluster template to create. %s') %
                 utils.NAME_DEPRECATION_HELP))
@utils.arg('--image-id',
           dest='image',
           required=True,
           metavar='<image>',
           help=utils.deprecation_message(
               'The name or UUID of the base image to customize for the '
               'Cluster.', 'image'))
@utils.arg('--image',
           dest='image',
           required=True,
           metavar='<image>',
           help=_('The name or UUID of the base image to customize for the '
                  'Cluster.'))
@utils.arg('--keypair-id',
           dest='keypair',
           metavar='<keypair>',
           help=utils.deprecation_message(
               'The name of the SSH keypair to load into the '
               'Cluster nodes.', 'keypair'))
@utils.arg('--keypair',
           dest='keypair',
           metavar='<keypair>',
           help=_('The name of the SSH keypair to load into the '
                  'Cluster nodes.'))
@utils.arg('--external-network-id',
           dest='external_network',
           required=True,
           metavar='<external-network>',
           help=utils.deprecation_message(
                'The external Neutron network name or UUID to connect to '
                'this Cluster Template.', 'external-network'))
@utils.arg('--external-network',
           dest='external_network',
           required=True,
           metavar='<external-network>',
           help=_('The external Neutron network name or UUID to connect to '
                  'this Cluster Template.'))
@utils.arg('--coe',
           required=True,
           metavar='<coe>',
           help=_('Specify the Container Orchestration Engine to use.'))
@utils.arg('--fixed-network',
           metavar='<fixed-network>',
           help=_('The private Neutron network name to connect to this Cluster'
                  ' model.'))
@utils.arg('--fixed-subnet',
           metavar='<fixed-subnet>',
           help=_('The private Neutron subnet name to connect to Cluster.'))
@utils.arg('--network-driver',
           metavar='<network-driver>',
           help=_('The network driver name for instantiating container'
                  ' networks.'))
@utils.arg('--volume-driver',
           metavar='<volume-driver>',
           help=_('The volume driver name for instantiating container'
                  ' volume.'))
@utils.arg('--dns-nameserver',
           metavar='<dns-nameserver>',
           default='8.8.8.8',
           help=_('The DNS nameserver to use for this cluster template.'))
@utils.arg('--flavor-id',
           dest='flavor',
           metavar='<flavor>',
           default='m1.medium',
           help=utils.deprecation_message(
                'The nova flavor name or UUID to use when launching the '
                'Cluster.', 'flavor'))
@utils.arg('--flavor',
           dest='flavor',
           metavar='<flavor>',
           default='m1.medium',
           help=_('The nova flavor name or UUID to use when launching the '
                  'Cluster.'))
@utils.arg('--master-flavor-id',
           dest='master_flavor',
           metavar='<master-flavor>',
           help=utils.deprecation_message(
                'The nova flavor name or UUID to use when launching the master'
                ' node of the Cluster.', 'master-flavor'))
@utils.arg('--master-flavor',
           dest='master_flavor',
           metavar='<master-flavor>',
           help=_('The nova flavor name or UUID to use when launching the'
                  ' master node of the Cluster.'))
@utils.arg('--docker-volume-size',
           metavar='<docker-volume-size>',
           type=int,
           help=_('Specify the number of size in GB '
                  'for the docker volume to use.'))
@utils.arg('--docker-storage-driver',
           metavar='<docker-storage-driver>',
           default='devicemapper',
           help=_('Select a docker storage driver. Supported: devicemapper, '
                  'overlay. Default: devicemapper'))
@utils.arg('--http-proxy',
           metavar='<http-proxy>',
           help=_('The http_proxy address to use for nodes in Cluster.'))
@utils.arg('--https-proxy',
           metavar='<https-proxy>',
           help=_('The https_proxy address to use for nodes in Cluster.'))
@utils.arg('--no-proxy',
           metavar='<no-proxy>',
           help=_('The no_proxy address to use for nodes in Cluster.'))
@utils.arg('--labels', metavar='<KEY1=VALUE1,KEY2=VALUE2;KEY3=VALUE3...>',
           action='append', default=[],
           help=_('Arbitrary labels in the form of key=value pairs '
                  'to associate with a cluster template. '
                  'May be used multiple times.'))
@utils.arg('--tls-disabled',
           action='store_true', default=False,
           help=_('Disable TLS in the Cluster.'))
@utils.arg('--public',
           action='store_true', default=False,
           help=_('Make cluster template public.'))
@utils.arg('--registry-enabled',
           action='store_true', default=False,
           help=_('Enable docker registry in the Cluster'))
@utils.arg('--server-type',
           metavar='<server-type>',
           default='vm',
           help=_('Specify the server type to be used '
                  'for example vm. For this release '
                  'default server type will be vm.'))
@utils.arg('--master-lb-enabled',
           action='store_true', default=False,
           help=_('Indicates whether created Clusters should have a load '
                  'balancer for master nodes or not.'))
@utils.arg('--floating-ip-enabled',
           action='store_true', default=True,
           help=_('Indicates whether created Clusters should have a '
                  'floating ip or not.'))
@utils.arg('--insecure-registry',
           metavar='<insecure-registry>',
           help='url of docker registry')
def do_cluster_template_create(cs, args):
    """Create a cluster template."""
    args.command = 'cluster-template-create'

    utils.validate_name_args(args.positional_name, args.name)

    opts = {}
    opts['name'] = args.positional_name or args.name
    opts['flavor_id'] = args.flavor
    opts['master_flavor_id'] = args.master_flavor
    opts['image_id'] = args.image
    opts['keypair_id'] = args.keypair
    opts['external_network_id'] = args.external_network
    opts['fixed_network'] = args.fixed_network
    opts['fixed_subnet'] = args.fixed_subnet
    opts['network_driver'] = args.network_driver
    opts['volume_driver'] = args.volume_driver
    opts['dns_nameserver'] = args.dns_nameserver
    opts['docker_volume_size'] = args.docker_volume_size
    opts['docker_storage_driver'] = args.docker_storage_driver
    opts['coe'] = args.coe
    opts['http_proxy'] = args.http_proxy
    opts['https_proxy'] = args.https_proxy
    opts['no_proxy'] = args.no_proxy
    opts['labels'] = magnum_utils.handle_labels(args.labels)
    opts['tls_disabled'] = args.tls_disabled
    opts['public'] = args.public
    opts['registry_enabled'] = args.registry_enabled
    opts['server_type'] = args.server_type
    opts['master_lb_enabled'] = args.master_lb_enabled
    opts['floating_ip_enabled'] = args.floating_ip_enabled
    opts['insecure_registry'] = args.insecure_registry

    cluster_template = cs.cluster_templates.create(**opts)
    _show_cluster_template(cluster_template)


@utils.arg('cluster_templates',
           metavar='<cluster_templates>',
           nargs='+',
           help=_('ID or name of the (cluster template)s to delete.'))
def do_cluster_template_delete(cs, args):
    """Delete specified cluster template."""
    for cluster_template in args.cluster_templates:
        try:
            cs.cluster_templates.delete(cluster_template)
            print("Request to delete cluster template %s has been accepted." %
                  cluster_template)
        except Exception as e:
            print("Delete for cluster template "
                  "%(cluster_template)s failed: %(e)s" %
                  {'cluster_template': cluster_template, 'e': e})


@utils.arg('cluster_template',
           metavar='<cluster_template>',
           help=_('ID or name of the cluster template to show.'))
def do_cluster_template_show(cs, args):
    """Show details about the given cluster template."""
    cluster_template = cs.cluster_templates.get(args.cluster_template)
    _show_cluster_template(cluster_template)


@utils.arg('--limit',
           metavar='<limit>',
           type=int,
           help=_('Maximum number of cluster templates to return'))
@utils.arg('--sort-key',
           metavar='<sort-key>',
           help=_('Column to sort results by'))
@utils.arg('--sort-dir',
           metavar='<sort-dir>',
           choices=['desc', 'asc'],
           help=_('Direction to sort. "asc" or "desc".'))
@utils.arg('--fields',
           default=None,
           metavar='<fields>',
           help=_('Comma-separated list of fields to display. '
                  'Available fields: uuid, name, coe, image_id, public, link, '
                  'apiserver_port, server_type, tls_disabled, registry_enabled'
                  )
           )
@utils.arg('--detail',
           action='store_true', default=False,
           help=_('Show detailed information about the cluster templates.')
           )
def do_cluster_template_list(cs, args):
    """Print a list of cluster templates."""
    nodes = cs.cluster_templates.list(limit=args.limit,
                                      sort_key=args.sort_key,
                                      sort_dir=args.sort_dir,
                                      detail=args.detail)
    if args.detail:
        columns = basemodels.OUTPUT_ATTRIBUTES
    else:
        columns = ['uuid', 'name']
    columns += utils._get_list_table_columns_and_formatters(
        args.fields, nodes,
        exclude_fields=(c.lower() for c in columns))[0]
    utils.print_list(nodes, columns,
                     {'versions': magnum_utils.print_list_field('versions')},
                     sortby_index=None)


@utils.arg('cluster_template',
           metavar='<cluster_template>',
           help=_("UUID or name of cluster template"))
@utils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help=_("Operations: 'add', 'replace' or 'remove'"))
@utils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help=_("Attributes to add/replace or remove "
           "(only PATH is necessary on remove)"))
def do_cluster_template_update(cs, args):
    """Updates one or more cluster template attributes."""
    patch = magnum_utils.args_array_to_patch(args.op, args.attributes[0])

    cluster_template = cs.cluster_templates.update(args.cluster_template,
                                                   patch)
    _show_cluster_template(cluster_template)
