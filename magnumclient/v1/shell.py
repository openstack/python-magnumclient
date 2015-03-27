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
    columns = ('uuid', 'name', 'node_count', 'status')
    utils.print_list(bays, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--name',
           metavar='<name>',
           help='Name of the bay to create.')
@utils.arg('--baymodel-id',
           required=True,
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


@utils.arg('bay',
           metavar='<bay>',
           nargs='+',
           help='ID or name of the (bay)s to delete.')
def do_bay_delete(cs, args):
    """Delete specified bay."""
    for id in args.bay:
        try:
            cs.bays.delete(id)
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
           required=True,
           metavar='<image_id>',
           help='The name or UUID of the base image to customize for the bay.')
@utils.arg('--keypair-id',
           required=True,
           metavar='<keypair_id>',
           help='The name or UUID of the SSH keypair to load into the'
           ' Bay nodes.')
@utils.arg('--external-network-id',
           required=True,
           metavar='<external_network_id>',
           help='The external Neutron network ID to connect to this bay'
           ' model.')
@utils.arg('--fixed-network',
           metavar='<fixed_network>',
           help='The private Neutron network name to connect to this bay'
           ' model.')
@utils.arg('--ssh-authorized-key',
           metavar='<ssh_authorized_key>',
           help='The SSH authorized key to use')
@utils.arg('--dns-nameserver',
           metavar='<dns_nameserver>',
           default='8.8.8.8',
           help='The DNS nameserver to use for this Bay.')
@utils.arg('--flavor-id',
           metavar='<flavor_id>',
           default='m1.medium',
           help='The nova flavor id to use when launching the bay.')
@utils.arg('--master-flavor-id',
           metavar='<master_flavor_id>',
           help='The nova flavor id to use when launching the master node'
           'of the bay.')
@utils.arg('--docker-volume-size',
           metavar='<docker_volume_size>',
           help='Specify the size of the docker volume to use.')
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
    opts['dns_nameserver'] = args.dns_nameserver
    opts['docker_volume_size'] = args.docker_volume_size
    opts['ssh_authorized_key'] = args.ssh_authorized_key

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
@utils.arg('--bay',
           required=True,
           metavar='<bay>',
           help='ID or name of the bay.')
def do_pod_create(cs, args):
    """Create a pod."""
    bay = cs.bays.get(args.bay)

    opts = {}
    opts['manifest_url'] = args.manifest_url
    opts['bay_uuid'] = bay.uuid

    if args.manifest is not None and os.path.isfile(args.manifest):
        with open(args.manifest, 'r') as f:
            opts['manifest'] = f.read()

    node = cs.pods.create(**opts)
    _show_pod(node)
    pass


@utils.arg('pods',
           metavar='<pods>',
           nargs='+',
           help='ID or name of the (pod)s to delete.')
def do_pod_delete(cs, args):
    """Delete specified pod."""
    for pod in args.pods:
        try:
            cs.pods.delete(pod)
        except Exception as e:
            print("Delete for pod %(pod)s failed: %(e)s" %
                  {'pod': pod, 'e': e})
    pass


@utils.arg('pod',
           metavar='<pod>',
           help='ID or name of the pod to show.')
def do_pod_show(cs, args):
    """Show details about the given pod."""
    pod = cs.pods.get(args.pod)
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


@utils.arg('rcs',
           metavar='<rcs>',
           nargs='+',
           help='ID or name of the replication (controller)s to delete.')
def do_rc_delete(cs, args):
    """Delete specified replication controller."""
    for rc in args.rcs:
        try:
            cs.rcs.delete(rc)
        except Exception as e:
            print("Delete for rc %(rc)s failed: %(e)s" %
                  {'rc': rc, 'e': e})


@utils.arg('rc',
           metavar='<rc>',
           help='ID or name of the replication controller to show.')
def do_rc_show(cs, args):
    """Show details about the given replication controller."""
    rc = cs.rcs.get(args.rc)
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


@utils.arg('services',
           metavar='<services>',
           nargs='+',
           help='ID or name of the (service)s to delete.')
def do_service_delete(cs, args):
    """Delete specified service."""
    for service in args.services:
        try:
            cs.services.delete(service)
        except Exception as e:
            print("Delete for service %(service)s failed: %(e)s" %
                  {'service': service, 'e': e})


@utils.arg('service',
           metavar='<service>',
           help='ID or name of the service to show.')
def do_service_show(cs, args):
    """Show details about the given service."""
    service = cs.services.get(args.service)
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


@utils.arg('id',
           metavar='<container_id>',
           nargs='+',
           help='ID of the (container)s to delete.')
def do_container_delete(cs, args):
    """Delete specified container."""
    for id in args.id:
        try:
            cs.containers.delete(id)
        except Exception as e:
            print("Delete for container %(container)s failed: %(e)s" %
                  {'container': id, 'e': e})


@utils.arg('id',
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


@utils.arg('id',
           metavar='<container_id>',
           nargs='+',
           help='ID of the (container)s to start.')
def do_container_reboot(cs, args):
    """Reboot specified container."""
    for id in args.id:
        try:
            cs.containers.reboot(id)
        except Exception as e:
            print("Reboot for container %(container)s failed: %(e)s" %
                  {'container': id, 'e': e})


@utils.arg('id',
           metavar='<container_id>',
           nargs='+',
           help='ID of the (container)s to start.')
def do_container_stop(cs, args):
    """Stop specified container."""
    for id in args.id:
        try:
            cs.containers.stop(id)
        except Exception as e:
            print("Stop for container %(container)s failed: %(e)s" %
                  {'container': id, 'e': e})


@utils.arg('id',
           metavar='<container_id>',
           nargs='+',
           help='ID of the (container)s to start.')
def do_container_start(cs, args):
    """Start specified container."""
    for id in args.id:
        try:
            cs.containers.start(id)
        except Exception as e:
            print("Start for container %(container)s failed: %(e)s" %
                  {'container': id, 'e': e})


@utils.arg('id',
           metavar='<container_id>',
           nargs='+',
           help='ID of the (container)s to start.')
def do_container_pause(cs, args):
    """Pause specified container."""
    for id in args.id:
        try:
            cs.containers.pause(id)
        except Exception as e:
            print("Pause for container %(container)s failed: %(e)s" %
                  {'container': id, 'e': e})


@utils.arg('id',
           metavar='<container_id>',
           nargs='+',
           help='ID of the (container)s to start.')
def do_container_unpause(cs, args):
    """Unpause specified container."""
    for id in args.id:
        try:
            cs.containers.unpause(id)
        except Exception as e:
            print("Unpause for container %(container)s failed: %(e)s" %
                  {'container': id, 'e': e})


@utils.arg('id',
           metavar='<container_id>',
           help='ID of the container to start.')
def do_container_logs(cs, args):
    """Get logs of a container."""
    logs = cs.containers.logs(args.id)
    print(logs)


@utils.arg('id',
           metavar='<container_id>',
           help='ID of the container to start.')
@utils.arg('--command',
           required=True,
           metavar='<command>',
           help='The command to execute')
def do_container_execute(cs, args):
    """Execute command in a container."""
    output = cs.containers.execute(args.id, args.command)
    print(output)
