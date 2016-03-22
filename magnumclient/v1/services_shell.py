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

from magnumclient.common import cliutils as utils
from magnumclient.common import utils as magnum_utils


def _show_coe_service(service):
    utils.print_dict(service._info)


@utils.arg('--bay',
           required=True,
           metavar='<bay>',
           help="UUID or Name of Bay")
def do_coe_service_list(cs, args):
    """Print a list of coe services."""
    services = cs.services.list(args.bay)
    columns = ('uuid', 'name', 'bay_uuid')
    utils.print_list(services, columns,
                     {'versions': magnum_utils.print_list_field('versions')})


@utils.arg('--manifest-url',
           metavar='<manifest-url>',
           help='Name/URL of the service file to use for creating services.')
@utils.arg('--manifest',
           metavar='<manifest>',
           help='File path of the service file to use for creating services.')
@utils.arg('--bay',
           required=True,
           metavar='<bay>',
           help='Id or name of the bay.')
def do_coe_service_create(cs, args):
    """Create a coe service."""
    bay = cs.bays.get(args.bay)
    if bay.status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        print('Bay status for %s is: %s. We can not create a service in bay '
              'until the status is CREATE_COMPLETE or UPDATE_COMPLETE.' %
              (args.bay, bay.status))
        return

    opts = {}
    opts['manifest_url'] = args.manifest_url
    opts['bay_uuid'] = bay.uuid

    if args.manifest is not None and os.path.isfile(args.manifest):
        with open(args.manifest, 'r') as f:
            opts['manifest'] = f.read()

    service = cs.services.create(**opts)
    _show_coe_service(service)


@utils.arg('services', metavar='<services>', help="UUID or name of service")
@utils.arg('--bay', required=True,
           metavar='<bay>', help="UUID or Name of Bay")
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
def do_coe_service_update(cs, args):
    """Update information about the given coe service."""
    patch = magnum_utils.args_array_to_patch(args.op, args.attributes[0])
    p = patch[0]
    if p['path'] == '/manifest' and os.path.isfile(p['value']):
        with open(p['value'], 'r') as f:
            p['value'] = f.read()

    service = cs.services.update(args.services, args.bay, patch)
    _show_coe_service(service)


@utils.arg('services', metavar='<services>', nargs='+',
           help='ID or name of the service to delete.')
@utils.arg('--bay', required=True, metavar='<bay>',
           help="UUID or Name of Bay")
def do_coe_service_delete(cs, args):
    """Delete specified coe service."""
    for service in args.services:
        try:
            cs.services.delete(service, args.bay)
            print("Request to delete service %s has been accepted." %
                  service)
        except Exception as e:
            print("Delete for service %(service)s failed: %(e)s" %
                  {'service': service, 'e': e})


@utils.arg('services', metavar='<services>',
           help='ID or name of the service to show.')
@utils.arg('--bay', required=True,
           metavar='<bay>', help="UUID or Name of Bay")
def do_coe_service_show(cs, args):
    """Show details about the given coe service."""
    service = cs.services.get(args.services, args.bay)
    _show_coe_service(service)
