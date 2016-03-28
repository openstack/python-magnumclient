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
from magnumclient import exceptions


def _show_rc(rc):
    utils.print_dict(rc._info)


@utils.arg('--bay', required=True,
           metavar='<bay>', help="UUID or Name of Bay")
def do_rc_list(cs, args):
    """Print a list of registered replication controllers."""
    bay = cs.bays.get(args.bay)
    if bay.status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        raise exceptions.InvalidAttribute(
            'Bay status for %s is: %s. We cannot list '
            'replication controllers in bay until the bay status '
            'is CREATE_COMPLETE or UPDATE_COMPLETE.' %
            (args.bay, bay.status))

    rcs = cs.rcs.list(args.bay)
    columns = ('uuid', 'name', 'bay_uuid')
    utils.print_list(rcs, columns,
                     {'versions': magnum_utils.print_list_field('versions')})


@utils.arg('--manifest-url',
           metavar='<manifest-url>',
           help='Name/URL of the replication controller file to use for '
                'creating replication controllers.')
@utils.arg('--manifest',
           metavar='<manifest>',
           help='File path of the replication controller file to use for '
                'creating replication controllers.')
@utils.arg('--bay',
           required=True,
           metavar='<bay>',
           help='ID or name of the bay.')
def do_rc_create(cs, args):
    """Create a replication controller."""
    bay = cs.bays.get(args.bay)
    if bay.status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        raise exceptions.InvalidAttribute(
            'Bay status for %s is: %s. We cannot create a '
            'replication controller in bay until the status '
            'is CREATE_COMPLETE or UPDATE_COMPLETE.' %
            (args.bay, bay.status))

    opts = {}
    opts['manifest_url'] = args.manifest_url
    opts['bay_uuid'] = bay.uuid

    if args.manifest is not None and os.path.isfile(args.manifest):
        with open(args.manifest, 'r') as f:
            opts['manifest'] = f.read()

    rc = cs.rcs.create(**opts)
    _show_rc(rc)


@utils.arg('rc', metavar='<rc>', help="UUID or name of replication controller")
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
def do_rc_update(cs, args):
    """Update information about the given replication controller."""
    patch = magnum_utils.args_array_to_patch(args.op, args.attributes[0])
    p = patch[0]
    if p['path'] == '/manifest' and os.path.isfile(p['value']):
        with open(p['value'], 'r') as f:
            p['value'] = f.read()

    rc = cs.rcs.update(args.rc, args.bay, patch)
    _show_rc(rc)


@utils.arg('rcs',
           metavar='<rcs>',
           nargs='+',
           help='ID or name of the replication (controller)s to delete.')
@utils.arg('--bay', required=True,
           metavar='<bay>', help="UUID or Name of Bay")
def do_rc_delete(cs, args):
    """Delete specified replication controller."""
    for rc in args.rcs:
        try:
            cs.rcs.delete(rc, args.bay)
            print("Request to delete rc %s has been accepted." %
                  rc)
        except Exception as e:
            print("Delete for rc %(rc)s failed: %(e)s" %
                  {'rc': rc, 'e': e})


@utils.arg('rc',
           metavar='<rc>',
           help='ID or name of the replication controller to show.')
@utils.arg('--bay', required=True,
           metavar='<bay>', help="UUID or Name of Bay")
def do_rc_show(cs, args):
    """Show details about the given replication controller."""
    rc = cs.rcs.get(args.rc, args.bay)
    _show_rc(rc)
