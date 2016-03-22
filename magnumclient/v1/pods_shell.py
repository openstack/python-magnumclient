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


def _show_pod(pod):
    del pod._info['links']
    utils.print_dict(pod._info)


@utils.arg('--bay', required=True,
           metavar='<bay>', help="UUID or Name of Bay")
def do_pod_list(cs, args):
    """Print a list of registered pods."""
    bay = cs.bays.get(args.bay)
    if bay.status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        raise exceptions.InvalidAttribute(
            'Bay status for %s is: %s. We can not list pods in there until'
            ' the status is CREATE_COMPLETE or UPDATE_COMPLETE.' %
            (bay.uuid, bay.status))
    pods = cs.pods.list(args.bay)
    columns = ('uuid', 'name')
    utils.print_list(pods, columns,
                     {'versions': magnum_utils.print_list_field('versions')})


@utils.arg('--manifest-url',
           metavar='<manifest-url>',
           help='Name/URL of the pod file to use for creating PODs.')
@utils.arg('--manifest',
           metavar='<manifest>',
           help='File path of the pod file to use for creating PODs.')
@utils.arg('--bay',
           required=True,
           metavar='<bay>',
           help='ID or name of the bay.')
def do_pod_create(cs, args):
    """Create a pod."""
    bay = cs.bays.get(args.bay)
    if bay.status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        raise exceptions.InvalidAttribute(
            'Bay status for %s is: %s. We cannot create a %s'
            ' until the status is CREATE_COMPLETE or UPDATE_COMPLETE.' %
            (bay.uuid, bay.status, "pod"))
    opts = {}
    opts['manifest_url'] = args.manifest_url
    opts['bay_uuid'] = bay.uuid

    if args.manifest is not None and os.path.isfile(args.manifest):
        with open(args.manifest, 'r') as f:
            opts['manifest'] = f.read()

    node = cs.pods.create(**opts)
    _show_pod(node)
    pass


@utils.arg('pod', metavar='<pod-id>', help="UUID or name of pod")
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
def do_pod_update(cs, args):
    """Update information about the given pod."""
    patch = magnum_utils.args_array_to_patch(args.op, args.attributes[0])
    p = patch[0]
    if p['path'] == '/manifest' and os.path.isfile(p['value']):
        with open(p['value'], 'r') as f:
            p['value'] = f.read()

    pod = cs.pods.update(args.pod, args.bay, patch)
    _show_pod(pod)


@utils.arg('pods',
           metavar='<pods>', nargs='+',
           help='ID or name of the (pod)s to delete.')
@utils.arg('--bay', required=True,
           metavar='<bay>', help="UUID or Name of Bay")
def do_pod_delete(cs, args):
    """Delete specified pod."""
    for pod in args.pods:
        try:
            cs.pods.delete(pod, args.bay)
            print("Request to delete pod %s has been accepted." %
                  pod)
        except Exception as e:
            print("Delete for pod %(pod)s failed: %(e)s" %
                  {'pod': pod, 'e': e})
    pass


@utils.arg('pod',
           metavar='<pod>',
           help='ID or name of the pod to show.')
@utils.arg('--bay', required=True,
           metavar='<bay>', help="UUID or Name of Bay")
def do_pod_show(cs, args):
    """Show details about the given pod."""
    pod = cs.pods.get(args.pod, args.bay)
    _show_pod(pod)
