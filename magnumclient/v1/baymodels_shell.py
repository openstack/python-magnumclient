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

import os.path

from magnumclient.common.apiclient import exceptions
from magnumclient.common import cliutils as utils
from magnumclient.common import utils as magnum_utils
from magnumclient.i18n import _


def _show_baymodel(baymodel):
    del baymodel._info['links']
    utils.print_dict(baymodel._info)


@utils.arg('--name',
           metavar='<name>',
           help='Name of the baymodel to create.')
@utils.arg('--image-id',
           required=True,
           metavar='<image-id>',
           help='The name or UUID of the base image to customize for the bay.')
@utils.arg('--keypair-id',
           required=True,
           metavar='<keypair-id>',
           help='The name or UUID of the SSH keypair to load into the'
           ' Bay nodes.')
@utils.arg('--external-network-id',
           required=True,
           metavar='<external-network-id>',
           help='The external Neutron network ID to connect to this bay'
           ' model.')
@utils.arg('--coe',
           required=True,
           metavar='<coe>',
           help='Specify the Container Orchestration Engine to use.')
@utils.arg('--fixed-network',
           metavar='<fixed-network>',
           help='The private Neutron network name to connect to this bay'
           ' model.')
@utils.arg('--network-driver',
           metavar='<network-driver>',
           help='The network driver name for instantiating container'
           ' networks.')
@utils.arg('--volume-driver',
           metavar='<volume-driver>',
           help='The volume driver name for instantiating container'
           ' volume.')
@utils.arg('--dns-nameserver',
           metavar='<dns-nameserver>',
           default='8.8.8.8',
           help='The DNS nameserver to use for this Bay.')
@utils.arg('--flavor-id',
           metavar='<flavor-id>',
           default='m1.medium',
           help='The nova flavor id to use when launching the bay.')
@utils.arg('--master-flavor-id',
           metavar='<master-flavor-id>',
           help='The nova flavor id to use when launching the master node '
           'of the bay.')
@utils.arg('--docker-volume-size',
           metavar='<docker-volume-size>',
           type=int,
           help='Specify the number of size in GB '
                'for the docker volume to use.')
@utils.arg('--http-proxy',
           metavar='<http-proxy>',
           help='The http_proxy address to use for nodes in bay.')
@utils.arg('--https-proxy',
           metavar='<https-proxy>',
           help='The https_proxy address to use for nodes in bay.')
@utils.arg('--no-proxy',
           metavar='<no-proxy>',
           help='The no_proxy address to use for nodes in bay.')
@utils.arg('--labels', metavar='<KEY1=VALUE1,KEY2=VALUE2;KEY3=VALUE3...>',
           action='append', default=[],
           help='Arbitrary labels in the form of key=value pairs '
                'to associate with a baymodel. '
                'May be used multiple times.')
@utils.arg('--tls-disabled',
           action='store_true', default=False,
           help='Disable TLS in the Bay.')
@utils.arg('--public',
           action='store_true', default=False,
           help='Make baymodel public.')
@utils.arg('--registry-enabled',
           action='store_true', default=False,
           help='Enable docker registry in the Bay')
def do_baymodel_create(cs, args):
    """Create a baymodel."""
    opts = {}
    opts['name'] = args.name
    opts['flavor_id'] = args.flavor_id
    opts['master_flavor_id'] = args.master_flavor_id
    opts['image_id'] = args.image_id
    opts['keypair_id'] = args.keypair_id
    opts['external_network_id'] = args.external_network_id
    opts['fixed_network'] = args.fixed_network
    opts['network_driver'] = args.network_driver
    opts['volume_driver'] = args.volume_driver
    opts['dns_nameserver'] = args.dns_nameserver
    opts['docker_volume_size'] = args.docker_volume_size
    opts['coe'] = args.coe
    opts['http_proxy'] = args.http_proxy
    opts['https_proxy'] = args.https_proxy
    opts['no_proxy'] = args.no_proxy
    opts['labels'] = magnum_utils.format_labels(args.labels)
    opts['tls_disabled'] = args.tls_disabled
    opts['public'] = args.public
    opts['registry_enabled'] = args.registry_enabled

    baymodel = cs.baymodels.create(**opts)
    _show_baymodel(baymodel)


@utils.arg('baymodels',
           metavar='<baymodels>',
           nargs='+',
           help='ID or name of the (baymodel)s to delete.')
def do_baymodel_delete(cs, args):
    """Delete specified baymodel."""
    for baymodel in args.baymodels:
        try:
            cs.baymodels.delete(baymodel)
            print("Request to delete baymodel %s has been accepted." %
                  baymodel)
        except Exception as e:
            print("Delete for baymodel %(baymodel)s failed: %(e)s" %
                  {'baymodel': baymodel, 'e': e})


@utils.arg('baymodel',
           metavar='<baymodel>',
           help='ID of the baymodel to show.')
def do_baymodel_show(cs, args):
    """Show details about the given baymodel."""
    baymodel = cs.baymodels.get(args.baymodel)
    _show_baymodel(baymodel)


@utils.arg('--limit',
           metavar='<limit>',
           type=int,
           help='Maximum number of baymodels to return')
@utils.arg('--sort-key',
           metavar='<sort-key>',
           help='Column to sort results by')
@utils.arg('--sort-dir',
           metavar='<sort-dir>',
           choices=['desc', 'asc'],
           help='Direction to sort. "asc" or "desc".')
@utils.arg('--fields',
           default=None,
           metavar='<fields>',
           help=_('Comma-separated list of fields to display. '
                  'Available fields: uuid, name, coe, image_id, public, link, '
                  'apiserver_port, server_type, tls_disabled, registry_enabled'
                  )
           )
def do_baymodel_list(cs, args):
    """Print a list of bay models."""
    nodes = cs.baymodels.list(limit=args.limit,
                              sort_key=args.sort_key,
                              sort_dir=args.sort_dir)
    columns = ['uuid', 'name']
    columns += _get_list_table_columns_and_formatters(
        args.fields, nodes,
        exclude_fields=(c.lower() for c in columns))[0]
    utils.print_list(nodes, columns,
                     {'versions': magnum_utils.print_list_field('versions')},
                     sortby_index=None)


@utils.arg('baymodel', metavar='<baymodel>', help="UUID or name of baymodel")
@utils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help="Operations: 'add', 'replace' or 'remove'")
@utils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help="Attributes to add/replace or remove "
         "(only PATH is necessary on remove)")
def do_baymodel_update(cs, args):
    """Updates one or more baymodel attributes."""
    patch = magnum_utils.args_array_to_patch(args.op, args.attributes[0])
    p = patch[0]
    if p['path'] == '/manifest' and os.path.isfile(p['value']):
        with open(p['value'], 'r') as f:
            p['value'] = f.read()

    baymodel = cs.baymodels.update(args.baymodel, patch)
    _show_baymodel(baymodel)


def _get_list_table_columns_and_formatters(fields, objs, exclude_fields=(),
                                           filters=None):
    """Check and add fields to output columns.

    If there is any value in fields that not an attribute of obj,
    CommandError will be raised.
    If fields has duplicate values (case sensitive), we will make them unique
    and ignore duplicate ones.
    :param fields: A list of string contains the fields to be printed.
    :param objs: An list of object which will be used to check if field is
                 valid or not. Note, we don't check fields if obj is None or
                 empty.
    :param exclude_fields: A tuple of string which contains the fields to be
                           excluded.
    :param filters: A dictionary defines how to get value from fields, this
                    is useful when field's value is a complex object such as
                    dictionary.
    :return: columns, formatters.
             columns is a list of string which will be used as table header.
             formatters is a dictionary specifies how to display the value
             of the field.
             They can be [], {}.
    :raise: magnumclient.common.apiclient.exceptions.CommandError.
    """

    if objs and isinstance(objs, list):
        obj = objs[0]
    else:
        obj = None
        fields = None

    columns = []
    formatters = {}

    if fields:
        non_existent_fields = []
        exclude_fields = set(exclude_fields)

        for field in fields.split(','):
            if not hasattr(obj, field):
                non_existent_fields.append(field)
                continue
            if field in exclude_fields:
                continue
            field_title, formatter = utils.make_field_formatter(field, filters)
            columns.append(field_title)
            formatters[field_title] = formatter
            exclude_fields.add(field)

        if non_existent_fields:
            raise exceptions.CommandError(
                _("Non-existent fields are specified: %s") %
                non_existent_fields
            )
    return columns, formatters
