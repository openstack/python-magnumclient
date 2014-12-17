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
import sys

from magnumclient.openstack.common import cliutils as utils


def _print_list_field(field):
    return lambda obj: ', '.join(getattr(obj, field))


def _show_container(container):
    utils.print_dict(container._info)


def _show_bay(bay):
    utils.print_dict(bay._info)


def _show_baymodel(baymodel):
    del baymodel._info['links']
    utils.print_dict(baymodel._info)


def _show_node(node):
    utils.print_dict(node._info)


def do_bay_list(cs, args):
    """Print a list of available bays."""
    bays = cs.bays.list()
    columns = ('uuid', 'name', 'type', 'image_id', 'node_count')
    utils.print_list(bays, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--name',
           metavar='<name>',
           help='Name of the bay to create.')
@utils.arg('--type',
           metavar='<type>',
           help='Type of bay to create (virt or bare).')
@utils.arg('--image_id',
           metavar='<image_id>',
           help='The name or UUID of the base image to customize for the bay.')
@utils.arg('--node_count',
           metavar='<node_count>',
           help='The bay node count.')
def do_bay_create(cs, args):
    """Create a bay."""
    opts = {}
    opts['name'] = args.name
    opts['type'] = args.type
    opts['image_id'] = args.image_id
    opts['node_count'] = args.node_count

    bay = cs.bays.create(**opts)
    _show_baymodel(bay)


@utils.arg('--id',
           metavar='<bay_id>',
           help='ID of the bay to delete.')
def do_bay_delete(cs, args):
    """Delete a bay."""
    cs.bays.delete(args.id)


@utils.arg('--id',
           metavar='<bay_id>',
           help='ID of the bay to show.')
def do_bay_show(cs, args):
    bay = cs.bays.get(args.id)
    _show_bay(bay)


@utils.arg('--name',
           metavar='<name>',
           help='Name of the bay to create.')
@utils.arg('--image_id',
           metavar='<image_id>',
           help='The name or UUID of the base image to customize for the bay.')
@utils.arg('--keypair_id',
           metavar='<keypair_id>',
           help='The name or UUID of the SSH keypair to load into the'
           ' Bay nodes.')
@utils.arg('--external_network_id',
           metavar='<external_network_id>',
           help='The external Neutron network ID to connect to this bay'
           ' model.')
@utils.arg('--dns_nameserver',
           metavar='<dns_nameserver>',
           help='The DNS nameserver to use for this Bay.')
def do_baymodel_create(cs, args):
    """Create a bay."""
    opts = {}
    opts['name'] = args.name
    opts['image_id'] = args.image_id
    opts['keypair_id'] = args.keypair_id
    opts['external_network_id'] = args.external_network_id
    opts['dns_nameserver'] = args.dns_nameserver

    bay = cs.baymodels.create(**opts)
    _show_baymodel(bay)


@utils.arg('--id',
           metavar='<bay_id>',
           help='ID of the bay to delete.')
def do_baymodel_delete(cs, args):
    """Delete a bay."""
    cs.baymodels.delete(args.id)


@utils.arg('--id',
           metavar='<bay_id>',
           help='ID of the bay to show.')
def do_baymodel_show(cs, args):
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
@utils.arg('--image_id',
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
    pass


def do_pod_create(cs, args):
    pass


def do_pod_delete(cs, args):
    pass


def do_pod_show(cs, args):
    pass


def do_service_list(cs, args):
    pass


def do_service_create(cs, args):
    pass


def do_service_delete(cs, args):
    pass


def do_service_show(cs, args):
    pass


#
# Containers
# ~~~~~~~~~~
# container-create [--json <file>]
#
# container-list
#
# container-delete --id <container_id>
#
# container-show --id <container_id> [--json]
#
# TODO(yuanying): container-reboot
#
# TODO(yuanying): container-stop
#
# TODO(yuanying): container-start
#
# TODO(yuanying): container-pause
#
# TODO(yuanying): container-unpause
#
# TODO(yuanying): container-logs
#
# TODO(yuanying): container-execute
#


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
    columns = ('container_id', 'name', 'desc')
    utils.print_list(containers, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--id',
           metavar='<container_id>',
           help='ID of the container to delete.')
def do_container_delete(cs, args):
    """Delete a container."""
    cs.containers.delete(args.id)


@utils.arg('--id',
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


def do_container_reboot(cs, args):
    pass


def do_container_stop(cs, args):
    pass


def do_container_start(cs, args):
    pass


def do_container_pause(cs, args):
    pass


def do_container_unpause(cs, args):
    pass


def do_container_logs(cs, args):
    pass


def do_container_execute(cs, args):
    pass
