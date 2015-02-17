# Copyright 2014
# The Cloudscaling Group, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import os.path
import sys

from magnumclient.common import utils as magnum_utils
from magnumclient.openstack.common import cliutils as utils


def _print_list_field(field):
    return lambda obj: ', '.join(getattr(obj, field))


def _show_container(container):
    utils.print_dict(container._info)


def _show_bay(bay):
    del bay._info['links']
    utils.print_dict(bay._info)


def _show_baymodel(baymodel):
    del baymodel._info['links']
    utils.print_dict(baymodel._info)


def _show_node(node):
    utils.print_dict(node._info)


def _show_pod(pod):
    utils.print_dict(pod._info)


def _show_rc(rc):
    utils.print_dict(rc._info)


def _show_service(service):
    utils.print_dict(service._info)


def do_bay_list(cs, args):
    """Print a list of available bays."""
    bays = cs.bays.list()
    columns = ('uuid', 'name', 'node_count')
    utils.print_list(bays, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--name',
           metavar='<name>',
           help='Name of the bay to create.')
@utils.arg('--baymodel-id',
           metavar='<baymodel_id>',
           help='The bay model ID.')
@utils.arg('--node-count',
           metavar='<node_count>',
           help='The bay node count.')
def do_bay_create(cs, args):
    """Create a bay."""
    opts = {}
    opts['name'] = args.name
    opts['baymodel_id'] = args.baymodel_id
    opts['node_count'] = args.node_count

    bay = cs.bays.create(**opts)
    _show_baymodel(bay)


@utils.arg('--id',
           required=True,
           metavar='<bay_id>',
           help='ID of the bay to delete.')
def do_bay_delete(cs, args):
    """Delete a bay."""
    cs.bays.delete(args.id)


@utils.arg('--id',
           required=True,
           metavar='<bay_id>',
           help='ID of the bay to show.')
def do_bay_show(cs, args):
    """Show details about the given bay."""
    bay = cs.bays.get(args.id)
    _show_bay(bay)


@utils.arg('bay', metavar='<bay id>', help="UUID of bay")
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


@utils.arg('--name',
           metavar='<name>',
           help='Name of the bay to create.')
@utils.arg('--image-id',
           metavar='<image_id>',
           help='The name or UUID of the base image to customize for the bay.')
@utils.arg('--keypair-id',
           metavar='<keypair_id>',
           help='The name or UUID of the SSH keypair to load into the'
           ' Bay nodes.')
@utils.arg('--external-network-id',
           metavar='<external_network_id>',
           help='The external Neutron network ID to connect to this bay'
           ' model.')
@utils.arg('--dns-nameserver',
           metavar='<dns_nameserver>',
           help='The DNS nameserver to use for this Bay.')
@utils.arg('--flavor-id',
           metavar='<flavor_id>',
           help='The nova flavor id to use when launching the bay.')
def do_baymodel_create(cs, args):
    """Create a baymodel."""
    opts = {}
    opts['name'] = args.name
    opts['flavor_id'] = args.flavor_id
    opts['image_id'] = args.image_id
    opts['keypair_id'] = args.keypair_id
    opts['external_network_id'] = args.external_network_id
    opts['dns_nameserver'] = args.dns_nameserver

    bay = cs.baymodels.create(**opts)
    _show_baymodel(bay)


@utils.arg('--id',
           metavar='<baymodel_id>',
           help='ID of the baymodel to delete.')
def do_baymodel_delete(cs, args):
    """Delete a baymodel."""
    cs.baymodels.delete(args.id)


@utils.arg('--id',
           metavar='<baymodel_id>',
           help='ID of the baymodel to show.')
def do_baymodel_show(cs, args):
    """Show details about the given baymodel."""
    baymodel = cs.baymodels.get(args.id)
    _show_baymodel(baymodel)


def do_baymodel_list(cs, args):
    """Print a list of bay models."""
    nodes = cs.baymodels.list()
    columns = ('uuid', 'name')
    utils.print_list(nodes, columns,
                     {'versions': _print_list_field('versions')})


def do_node_list(cs, args):
    """Print a list of configured nodes."""
    nodes = cs.nodes.list()
    columns = ('uuid', 'type', 'image_id')
    utils.print_list(nodes, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--type',
           metavar='<type>',
           help='Type of node to create (virt or bare).')
@utils.arg('--image-id',
           metavar='<image_id>',
           help='The name or UUID of the base image to use for the node.')
def do_node_create(cs, args):
    """Create a node."""
    opts = {}
    opts['type'] = args.type
    opts['image_id'] = args.image_id

    node = cs.nodes.create(**opts)
    _show_node(node)


def do_pod_list(cs, args):
    """Print a list of registered pods."""
    pods = cs.pods.list()
    columns = ('uuid', 'name')
    utils.print_list(pods, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--manifest-url',
           metavar='<manifest_url>',
           help='Name/URL of the pod file to use for creating PODs.')
@utils.arg('--manifest',
           metavar='<manifest>',
           help='File path of the pod file to use for creating PODs.')
@utils.arg('--bay-id',
           required=True,
           metavar='<bay_id>',
           help='The bay ID.')
def do_pod_create(cs, args):
    """Create a pod."""
    opts = {}
    opts['manifest_url'] = args.manifest_url
    opts['bay_uuid'] = args.bay_id

    if args.manifest is not None and os.path.isfile(args.manifest):
        with open(args.manifest, 'r') as f:
            opts['manifest'] = f.read()

    node = cs.pods.create(**opts)
    _show_pod(node)
    pass


@utils.arg('--id',
           required=True,
           metavar='<pod_id>',
           help='ID of the pod to delete.')
def do_pod_delete(cs, args):
    """Delete a pod."""
    cs.pods.delete(args.id)
    pass


@utils.arg('--id',
           required=True,
           metavar='<pod_id>',
           help='ID of the pod to show.')
def do_pod_show(cs, args):
    """Show details about the given pod."""
    pod = cs.pods.get(args.id)
    _show_pod(pod)


def do_rc_list(cs, args):
    """Print a list of registered replication controllers."""
    rcs = cs.rcs.list()
    columns = ('uuid', 'name')
    utils.print_list(rcs, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--manifest-url',
           metavar='<manifest_url>',
           help='Name/URL of the replication controller file to use for '
                'creating replication controllers.')
@utils.arg('--manifest',
           metavar='<manifest>',
           help='File path of the replication controller file to use for '
                'creating replication controllers.')
@utils.arg('--bay-id',
           required=True,
           metavar='<bay_id>',
           help='The bay ID.')
def do_rc_create(cs, args):
    """Create a replication controller."""
    opts = {}
    opts['manifest_url'] = args.manifest_url
    opts['bay_uuid'] = args.bay_id

    if args.manifest is not None and os.path.isfile(args.manifest):
        with open(args.manifest, 'r') as f:
            opts['manifest'] = f.read()

    rc = cs.rcs.create(**opts)
    _show_rc(rc)


@utils.arg('--id',
           required=True,
           metavar='<rc_id>',
           help='ID of the replication controller to delete.')
def do_rc_delete(cs, args):
    """Delete a replication controller."""
    cs.rcs.delete(args.id)


@utils.arg('--id',
           required=True,
           metavar='<rc_id>',
           help='ID of the replication controller to show.')
def do_rc_show(cs, args):
    """Show details about the given replication controller."""
    rc = cs.rcs.get(args.id)
    _show_rc(rc)


def do_service_list(cs, args):
    """Print a list of services."""
    services = cs.services.list()
    columns = ('uuid', 'name', 'bay_uuid')
    utils.print_list(services, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--manifest-url',
           metavar='<manifest_url>',
           help='Name/URL of the serivce file to use for creating services.')
@utils.arg('--manifest',
           metavar='<manifest>',
           help='File path of the service file to use for creating services.')
@utils.arg('--bay-id',
           required=True,
           metavar='<bay_id>',
           help='The bay ID.')
def do_service_create(cs, args):
    """Create a service."""
    opts = {}
    opts['manifest_url'] = args.manifest_url
    opts['bay_uuid'] = args.bay_id

    if args.manifest is not None and os.path.isfile(args.manifest):
        with open(args.manifest, 'r') as f:
            opts['manifest'] = f.read()

    service = cs.services.create(**opts)
    _show_service(service)


@utils.arg('--id',
           required=True,
           metavar='<service_id>',
           help='ID of the service to delete.')
def do_service_delete(cs, args):
    """Delete a service."""
    cs.services.delete(args.id)


@utils.arg('--id',
           required=True,
           metavar='<service_id>',
           help='ID of the service to show.')
def do_service_show(cs, args):
    """Show details about the given service."""
    service = cs.services.get(args.id)
    _show_service(service)


#
# Containers

@utils.arg('--json',
           default=sys.stdin,
           type=argparse.FileType('r'),
           help='JSON representation of container.')
def do_container_create(cs, args):
    """Create a container."""
    container = json.loads(args.json.read())
    _show_container(cs.containers.create(**container))


def do_container_list(cs, args):
    """Print a list of available containers."""
    containers = cs.containers.list()
    columns = ('uuid', 'name')
    utils.print_list(containers, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--id',
           required=True,
           metavar='<container_id>',
           help='ID of the container to delete.')
def do_container_delete(cs, args):
    """Delete a container."""
    cs.containers.delete(args.id)


@utils.arg('--id',
           required=True,
           metavar='<container_id>',
           help='ID of the container to show.')
@utils.arg('--json',
           action='store_true',
           default=False,
           help='Print JSON representation of the container.')
def do_container_show(cs, args):
    """Show details of a container."""
    container = cs.containers.get(args.id)
    if args.json:
        print(json.dumps(container._info))
    else:
        _show_container(container)


@utils.arg('--id',
           required=True,
           metavar='<container_id>',
           help='ID of the container to start.')
def do_container_reboot(cs, args):
    """Reboot a container."""
    cs.containers.reboot(args.id)


@utils.arg('--id',
           required=True,
           metavar='<container_id>',
           help='ID of the container to start.')
def do_container_stop(cs, args):
    """Stop a container."""
    cs.containers.stop(args.id)


@utils.arg('--id',
           required=True,
           metavar='<container_id>',
           help='ID of the container to start.')
def do_container_start(cs, args):
    """Start a container."""
    cs.containers.start(args.id)


@utils.arg('--id',
           required=True,
           metavar='<container_id>',
           help='ID of the container to start.')
def do_container_pause(cs, args):
    """Pause a container."""
    cs.containers.pause(args.id)


@utils.arg('--id',
           required=True,
           metavar='<container_id>',
           help='ID of the container to start.')
def do_container_unpause(cs, args):
    """Unpause a container."""
    cs.containers.unpause(args.id)


@utils.arg('--id',
           required=True,
           metavar='<container_id>',
           help='ID of the container to start.')
def do_container_logs(cs, args):
    """Get logs of a container."""
    cs.containers.logs(args.id)


@utils.arg('--id',
           required=True,
           metavar='<container_id>',
           help='ID of the container to start.')
@utils.arg('--command',
           required=True,
           metavar='<command>',
           help='The command to execute')
def do_container_execute(cs, args):
    """Execute command in a container."""
    cs.containers.execute(args.id, args.command)
