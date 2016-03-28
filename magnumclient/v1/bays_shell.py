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


def _show_bay(bay):
    del bay._info['links']
    utils.print_dict(bay._info)


@utils.arg('--marker',
           metavar='<marker>',
           default=None,
           help='The last bay UUID of the previous page; '
                'displays list of bays after "marker".')
@utils.arg('--limit',
           metavar='<limit>',
           type=int,
           help='Maximum number of bays to return.')
@utils.arg('--sort-key',
           metavar='<sort-key>',
           help='Column to sort results by.')
@utils.arg('--sort-dir',
           metavar='<sort-dir>',
           choices=['desc', 'asc'],
           help='Direction to sort. "asc" or "desc".')
def do_bay_list(cs, args):
    """Print a list of available bays."""
    bays = cs.bays.list(marker=args.marker, limit=args.limit,
                        sort_key=args.sort_key,
                        sort_dir=args.sort_dir)
    columns = ('uuid', 'name', 'node_count', 'master_count', 'status')
    utils.print_list(bays, columns,
                     {'versions': magnum_utils.print_list_field('versions')},
                     sortby_index=None)


@utils.arg('--name',
           metavar='<name>',
           help='Name of the bay to create.')
@utils.arg('--baymodel',
           required=True,
           metavar='<baymodel>',
           help='ID or name of the baymodel.')
@utils.arg('--node-count',
           metavar='<node-count>',
           type=int,
           default=1,
           help='The bay node count.')
@utils.arg('--master-count',
           metavar='<master-count>',
           type=int,
           default=1,
           help='The number of master nodes for the bay.')
@utils.arg('--discovery-url',
           metavar='<discovery-url>',
           help='Specifies custom discovery url for node discovery.')
@utils.arg('--timeout',
           metavar='<timeout>',
           type=int,
           default=0,
           help='The timeout for bay creation in minutes. Set '
                'to 0 for no timeout. The default is no timeout.')
def do_bay_create(cs, args):
    """Create a bay."""
    baymodel = cs.baymodels.get(args.baymodel)

    opts = {}
    opts['name'] = args.name
    opts['baymodel_id'] = baymodel.uuid
    opts['node_count'] = args.node_count
    opts['master_count'] = args.master_count
    opts['discovery_url'] = args.discovery_url
    opts['bay_create_timeout'] = args.timeout
    try:
        bay = cs.bays.create(**opts)
        _show_bay(bay)
    except Exception as e:
        print("Create for bay %s failed: %s" %
              (opts['name'], e))


@utils.arg('bay',
           metavar='<bay>',
           nargs='+',
           help='ID or name of the (bay)s to delete.')
def do_bay_delete(cs, args):
    """Delete specified bay."""
    for id in args.bay:
        try:
            cs.bays.delete(id)
            print("Request to delete bay %s has been accepted." %
                  id)
        except Exception as e:
            print("Delete for bay %(bay)s failed: %(e)s" %
                  {'bay': id, 'e': e})


@utils.arg('bay',
           metavar='<bay>',
           help='ID or name of the bay to show.')
def do_bay_show(cs, args):
    """Show details about the given bay."""
    bay = cs.bays.get(args.bay)
    _show_bay(bay)


@utils.arg('bay', metavar='<bay>', help="UUID or name of bay")
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
def do_bay_update(cs, args):
    """Update information about the given bay."""
    patch = magnum_utils.args_array_to_patch(args.op, args.attributes[0])
    bay = cs.bays.update(args.bay, patch)
    _show_bay(bay)
