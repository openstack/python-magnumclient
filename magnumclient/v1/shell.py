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

import json
import os.path

from magnumclient.common import utils as magnum_utils
from magnumclient.openstack.common import cliutils as utils


def _print_list_field(field):
    return lambda obj: ', '.join(getattr(obj, field))


def _show_container(container):
    utils.print_dict(container._info)


def _show_bay(bay):
    del bay._info['links']
    utils.print_dict(bay._info)


def _show_cert(certificate):
    print(certificate.pem)


def _show_baymodel(baymodel):
    del baymodel._info['links']
    utils.print_dict(baymodel._info)


def _show_node(node):
    utils.print_dict(node._info)


def _show_pod(pod):
    del pod._info['links']
    utils.print_dict(pod._info)


def _show_rc(rc):
    utils.print_dict(rc._info)


def _show_coe_service(service):
    utils.print_dict(service._info)


def do_bay_list(cs, args):
    """Print a list of available bays."""
    bays = cs.bays.list()
    columns = ('uuid', 'name', 'node_count', 'master_count', 'status')
    utils.print_list(bays, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--name',
           metavar='<name>',
           help='Name of the bay to create.')
@utils.arg('--baymodel',
           required=True,
           metavar='<baymodel>',
           help='ID or name of the baymodel.')
@utils.arg('--node-count',
           metavar='<node-count>',
           help='The bay node count.')
@utils.arg('--master-count',
           metavar='<master-count>',
           default=1,
           help='The number of master nodes for the bay.')
@utils.arg('--discovery-url',
           metavar='<discovery-url>',
           help='Specifies custom discovery url for node discovery.')
@utils.arg('--timeout',
           metavar='<timeout>',
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


@utils.arg('--name',
           metavar='<name>',
           help='Name of the bay to create.')
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
@utils.arg('--ssh-authorized-key',
           metavar='<ssh-authorized-key>',
           help='The SSH authorized key to use')
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
           help='Specify the size of the docker volume to use.')
@utils.arg('--http-proxy',
           metavar='<http-proxy>',
           help='The http_proxy address to use for nodes in bay.')
@utils.arg('--https-proxy',
           metavar='<https-proxy>',
           help='The https_proxy address to use for nodes in bay.')
@utils.arg('--no-proxy',
           metavar='<no-proxy>',
           help='The no_proxy address to use for nodes in bay.')
@utils.arg('--labels', metavar='<KEY1=VALUE1,KEY2=VALUE2...>',
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
    opts['dns_nameserver'] = args.dns_nameserver
    opts['docker_volume_size'] = args.docker_volume_size
    opts['ssh_authorized_key'] = args.ssh_authorized_key
    opts['coe'] = args.coe
    opts['http_proxy'] = args.http_proxy
    opts['https_proxy'] = args.https_proxy
    opts['no_proxy'] = args.no_proxy
    opts['labels'] = magnum_utils.format_labels(args.labels)
    opts['tls_disabled'] = args.tls_disabled
    opts['public'] = args.public

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


@utils.arg('--bay',
           required=True,
           metavar='<bay>',
           help='ID or name of the bay.')
def do_ca_show(cs, args):
    bay = cs.bays.get(args.bay)
    if bay.status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        print('Bay status for %s is: %s. We can not create a %s there'
              ' until the status is CREATE_COMPLETE or UPDATE_COMPLETE.' %
              (bay.uuid, bay.status, 'certificate'))
        return

    opts = {
        'bay_uuid': bay.uuid
    }

    cert = cs.certificates.get(**opts)
    _show_cert(cert)


@utils.arg('--csr',
           metavar='<csr>',
           help='File path of the csr file to send to Magnum to get signed.')
@utils.arg('--bay',
           required=True,
           metavar='<bay>',
           help='ID or name of the bay.')
def do_ca_sign(cs, args):
    bay = cs.bays.get(args.bay)
    if bay.status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        print('Bay status for %s is: %s. We can not create a %s there'
              ' until the status is CREATE_COMPLETE or UPDATE_COMPLETE.' %
              (bay.uuid, bay.status, 'certificate'))
        return

    opts = {
        'bay_uuid': bay.uuid
    }

    if args.csr is None or not os.path.isfile(args.csr):
        print('A CSR must be provided.')
        return

    with open(args.csr, 'r') as f:
        opts['csr'] = f.read()

    cert = cs.certificates.create(**opts)
    _show_cert(cert)


@utils.arg('baymodel', metavar='<baymodel>', help="UUID of baymodel")
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
           metavar='<image-id>',
           help='The name or UUID of the base image to use for the node.')
def do_node_create(cs, args):
    """Create a node."""
    opts = {}
    opts['type'] = args.type
    opts['image_id'] = args.image_id

    node = cs.nodes.create(**opts)
    _show_node(node)


@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
def do_pod_list(cs, args):
    """Print a list of registered pods."""
    pods = cs.pods.list(args.bay)
    columns = ('uuid', 'name')
    utils.print_list(pods, columns,
                     {'versions': _print_list_field('versions')})


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
        print('Bay status for %s is: %s. We can not create a %s there'
              ' until the status is CREATE_COMPLETE or UPDATE_COMPLETE.' %
              (bay.uuid, bay.status, "pod"))
        return
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
@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
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
           metavar='<pods>',
           nargs='+',
           help='ID or name of the (pod)s to delete.')
@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
def do_pod_delete(cs, args):
    """Delete specified pod."""
    for pod in args.pods:
        try:
            cs.pods.delete(pod, args.bay)
        except Exception as e:
            print("Delete for pod %(pod)s failed: %(e)s" %
                  {'pod': pod, 'e': e})
    pass


@utils.arg('pod',
           metavar='<pod>',
           help='ID or name of the pod to show.')
@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
def do_pod_show(cs, args):
    """Show details about the given pod."""
    pod = cs.pods.get(args.pod, args.bay)
    _show_pod(pod)


@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
def do_rc_list(cs, args):
    """Print a list of registered replication controllers."""
    rcs = cs.rcs.list(args.bay)
    columns = ('uuid', 'name')
    utils.print_list(rcs, columns,
                     {'versions': _print_list_field('versions')})


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
        print('Bay status for %s is: %s. We can not create a '
              'replication controller in bay until the status '
              'is CREATE_COMPLETE or UPDATE_COMPLETE.' %
              (args.bay, bay.status))
        return

    opts = {}
    opts['manifest_url'] = args.manifest_url
    opts['bay_uuid'] = bay.uuid

    if args.manifest is not None and os.path.isfile(args.manifest):
        with open(args.manifest, 'r') as f:
            opts['manifest'] = f.read()

    rc = cs.rcs.create(**opts)
    _show_rc(rc)


@utils.arg('rc', metavar='<rc>', help="UUID or name of replication controller")
@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
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
@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
def do_rc_delete(cs, args):
    """Delete specified replication controller."""
    for rc in args.rcs:
        try:
            cs.rcs.delete(rc, args.bay)
        except Exception as e:
            print("Delete for rc %(rc)s failed: %(e)s" %
                  {'rc': rc, 'e': e})


@utils.arg('rc',
           metavar='<rc>',
           help='ID or name of the replication controller to show.')
@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
def do_rc_show(cs, args):
    """Show details about the given replication controller."""
    rc = cs.rcs.get(args.rc, args.bay)
    _show_rc(rc)


@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
def do_coe_service_list(cs, args):
    """Print a list of coe services."""
    services = cs.services.list(args.bay)
    columns = ('uuid', 'name', 'bay_uuid')
    utils.print_list(services, columns,
                     {'versions': _print_list_field('versions')})


def do_service_list(cs, args):
    """Print a list of magnum services."""
    mservices = cs.mservices.list()
    columns = ('id', 'host', 'binary', 'state')
    utils.print_list(mservices, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--manifest-url',
           metavar='<manifest-url>',
           help='Name/URL of the serivce file to use for creating services.')
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


@utils.arg('service', metavar='<service>', help="UUID or name of service")
@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
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

    service = cs.services.update(args.service, args.bay, patch)
    _show_coe_service(service)


@utils.arg('services',
           metavar='<services>',
           nargs='+',
           help='ID or name of the (service)s to delete.')
@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
def do_coe_service_delete(cs, args):
    """Delete specified coe service(s)."""
    for service in args.services:
        try:
            cs.services.delete(service, args.bay)
        except Exception as e:
            print("Delete for service %(service)s failed: %(e)s" %
                  {'service': service, 'e': e})


@utils.arg('service',
           metavar='<service>',
           help='ID or name of the service to show.')
@utils.arg('bay', metavar='<bay>', help="UUID or Name of Bay")
def do_coe_service_show(cs, args):
    """Show details about the given coe service."""
    service = cs.services.get(args.service, args.bay)
    _show_coe_service(service)


#
# Containers

@utils.arg('--name',
           metavar='<name>',
           help='name of the container')
@utils.arg('--image',
           metavar='<image>',
           help='name or ID of the image')
@utils.arg('--bay',
           required=True,
           metavar='<bay>',
           help='ID or name of the bay.')
@utils.arg('--command',
           metavar='<command>',
           help='Send command to the container')
@utils.arg('--memory',
           metavar='<memory>',
           help='The container memory size (format: <number><optional unit>, '
                'where unit = b, k, m or g)')
def do_container_create(cs, args):
    """Create a container."""
    bay = cs.bays.get(args.bay)
    if bay.status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        print('Bay status for %s is: %s. We can not create a %s there'
              ' until the status is CREATE_COMPLETE or UPDATE_COMPLETE.' %
              (bay.uuid, bay.status, "pod"))
        return
    opts = {}
    opts['name'] = args.name
    opts['image'] = args.image
    opts['bay_uuid'] = bay.uuid
    opts['command'] = args.command
    opts['memory'] = args.memory
    _show_container(cs.containers.create(**opts))


def do_container_list(cs, args):
    """Print a list of available containers."""
    containers = cs.containers.list()
    columns = ('uuid', 'name', 'status')
    utils.print_list(containers, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('containers',
           metavar='<container>',
           nargs='+',
           help='ID or name of the (container)s to delete.')
def do_container_delete(cs, args):
    """Delete specified containers."""
    for container in args.containers:
        try:
            cs.containers.delete(container)
        except Exception as e:
            print("Delete for container %(container)s failed: %(e)s" %
                  {'container': container, 'e': e})


@utils.arg('container',
           metavar='<container>',
           help='ID or name of the container to show.')
@utils.arg('--json',
           action='store_true',
           default=False,
           help='Print JSON representation of the container.')
def do_container_show(cs, args):
    """Show details of a container."""
    container = cs.containers.get(args.container)
    if args.json:
        print(json.dumps(container._info))
    else:
        _show_container(container)


@utils.arg('containers',
           metavar='<container>',
           nargs='+',
           help='ID or name of the (container)s to start.')
def do_container_reboot(cs, args):
    """Reboot specified containers."""
    for container in args.containers:
        try:
            cs.containers.reboot(container)
        except Exception as e:
            print("Reboot for container %(container)s failed: %(e)s" %
                  {'container': container, 'e': e})


@utils.arg('containers',
           metavar='<container>',
           nargs='+',
           help='ID or name of the (container)s to start.')
def do_container_stop(cs, args):
    """Stop specified containers."""
    for container in args.containers:
        try:
            cs.containers.stop(container)
        except Exception as e:
            print("Stop for container %(container)s failed: %(e)s" %
                  {'container': container, 'e': e})


@utils.arg('containers',
           metavar='<container>',
           nargs='+',
           help='ID of the (container)s to start.')
def do_container_start(cs, args):
    """Start specified containers."""
    for container in args.containers:
        try:
            cs.containers.start(container)
        except Exception as e:
            print("Start for container %(container)s failed: %(e)s" %
                  {'container': container, 'e': e})


@utils.arg('containers',
           metavar='<container>',
           nargs='+',
           help='ID or name of the (container)s to start.')
def do_container_pause(cs, args):
    """Pause specified containers."""
    for container in args.containers:
        try:
            cs.containers.pause(container)
        except Exception as e:
            print("Pause for container %(container)s failed: %(e)s" %
                  {'container': container, 'e': e})


@utils.arg('containers',
           metavar='<container>',
           nargs='+',
           help='ID or name of the (container)s to start.')
def do_container_unpause(cs, args):
    """Unpause specified containers."""
    for container in args.containers:
        try:
            cs.containers.unpause(container)
        except Exception as e:
            print("Unpause for container %(container)s failed: %(e)s" %
                  {'container': container, 'e': e})


@utils.arg('container',
           metavar='<container>',
           help='ID or name of the container to start.')
def do_container_logs(cs, args):
    """Get logs of a container."""
    logs = cs.containers.logs(args.container)
    print(logs)


@utils.arg('container',
           metavar='<container>',
           help='ID or name of the container to start.')
@utils.arg('--command',
           required=True,
           metavar='<command>',
           help='The command to execute')
def do_container_exec(cs, args):
    """Execute command in a container."""
    output = cs.containers.execute(args.container, args.command)
    print(output)
