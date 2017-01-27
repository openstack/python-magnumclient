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


def _show_quota(quota):
    utils.print_dict(quota._info)


@utils.arg('--marker',
           metavar='<marker>',
           default=None,
           help=_('The last quota UUID of the previous page; '
                  'displays list of quotas after "marker".'))
@utils.arg('--limit',
           metavar='<limit>',
           type=int,
           help=_('Maximum number of quotas to return.'))
@utils.arg('--sort-key',
           metavar='<sort-key>',
           help=_('Column to sort results by.'))
@utils.arg('--sort-dir',
           metavar='<sort-dir>',
           choices=['desc', 'asc'],
           help=_('Direction to sort. "asc" or "desc".'))
@utils.arg('--all-tenants',
           action='store_true',
           default=False,
           help=_('Flag to indicate list all tenant quotas.'))
def do_quotas_list(cs, args):
    """Print a list of available quotas."""
    quotas = cs.quotas.list(marker=args.marker,
                            limit=args.limit,
                            sort_key=args.sort_key,
                            sort_dir=args.sort_dir,
                            all_tenants=args.all_tenants)
    columns = ['project_id', 'resource', 'hard_limit']
    utils.print_list(quotas, columns,
                     {'versions': magnum_utils.print_list_field('versions')},
                     sortby_index=None)


@utils.arg('--project-id',
           required=True,
           metavar='<project-id>',
           help=_('Project Id.'))
@utils.arg('--resource',
           required=True,
           metavar='<resource>',
           help=_('Resource name.'))
@utils.arg('--hard-limit',
           metavar='<hard-limit>',
           type=int,
           default=1,
           help=_('Max resource limit.'))
def do_quotas_create(cs, args):
    """Create a quota."""

    opts = dict()
    opts['project_id'] = args.project_id
    opts['resource'] = args.resource
    opts['hard_limit'] = args.hard_limit

    try:
        quota = cs.quotas.create(**opts)
        _show_quota(quota)
    except Exception as e:
        print("Create quota for project_id %(id)s resource %(res)s failed: "
              "%(e)s" % {'id': args.project_id,
                         'res': args.resource,
                         'e': e.details})


@utils.arg('--project-id',
           required=True,
           metavar='<project-id>',
           help=_('Project ID.'))
@utils.arg('--resource',
           required=True,
           metavar='<resource>',
           help=_('Resource name'))
def do_quotas_delete(cs, args):
    """Delete specified resource quota."""
    try:
        cs.quotas.delete(args.project_id, args.resource)
        print("Request to delete quota for project id %(id)s and resource "
              "%(res)s has been accepted." % {
                  'id': args.project_id, 'res': args.resource})
    except Exception as e:
        print("Quota delete failed for project id %(id)s and resource "
              "%(res)s :%(e)s" % {'id': args.project_id,
                                  'res': args.resource,
                                  'e': e.details})


@utils.arg('--project-id',
           required=True,
           metavar='<project-id>',
           help=_('Project ID.'))
@utils.arg('--resource',
           required=True,
           metavar='<resource>',
           help=_('Resource name'))
def do_quotas_show(cs, args):
    """Show details about the given project resource quota."""
    quota = cs.quotas.get(args.project_id, args.resource)
    _show_quota(quota)


@utils.arg('--project-id',
           required=True,
           metavar='<project-id>',
           help=_('Project Id.'))
@utils.arg('--resource',
           required=True,
           metavar='<resource>',
           help=_('Resource name.'))
@utils.arg('--hard-limit',
           metavar='<hard-limit>',
           type=int,
           default=1,
           help=_('Max resource limit.'))
def do_quotas_update(cs, args):
    """Update information about the given project resource quota."""
    patch = dict()
    patch['project_id'] = args.project_id
    patch['resource'] = args.resource
    patch['hard_limit'] = args.hard_limit

    quota = cs.quotas.update(args.project_id, args.resource, patch)
    _show_quota(quota)
