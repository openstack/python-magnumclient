# Copyright (c) 2018 European Organization for Nuclear Research.
# All Rights Reserved.
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

from magnumclient.common import utils as magnum_utils
from magnumclient.i18n import _

from osc_lib.command import command
from osc_lib import utils


NODEGROUP_ATTRIBUTES = [
    'uuid',
    'name',
    'cluster_id',
    'project_id',
    'docker_volume_size',
    'labels',
    'flavor_id',
    'image_id',
    'node_addresses',
    'node_count',
    'role',
    'max_node_count',
    'min_node_count',
    'is_default',
    'stack_id',
    'status',
    'status_reason'
]


class CreateNodeGroup(command.Command):
    _description = _("Create a nodegroup")

    def get_parser(self, prog_name):
        parser = super(CreateNodeGroup, self).get_parser(prog_name)
        # NOTE: All arguments are positional and, if not provided
        # with a default, required.
        parser.add_argument('--docker-volume-size',
                            dest='docker_volume_size',
                            type=int,
                            metavar='<docker-volume-size>',
                            help=('The size in GB for the docker volume to '
                                  'use.'))
        parser.add_argument('--labels',
                            metavar='<KEY1=VALUE1,KEY2=VALUE2;KEY3=VALUE3...>',
                            action='append',
                            help=_('Arbitrary labels in the form of key=value'
                                   'pairs to associate with a nodegroup. '
                                   'May be used multiple times.'))
        parser.add_argument('cluster',
                            metavar='<cluster>',
                            help='Name of the nodegroup to create.')
        parser.add_argument('name',
                            metavar='<name>',
                            help='Name of the nodegroup to create.')
        parser.add_argument('--node-count',
                            dest='node_count',
                            type=int,
                            default=1,
                            metavar='<node-count>',
                            help='The nodegroup node count.')
        parser.add_argument('--min-nodes',
                            dest='min_node_count',
                            type=int,
                            default=1,
                            metavar='<min-nodes>',
                            help='The nodegroup minimum node count.')
        parser.add_argument('--max-nodes',
                            dest='max_node_count',
                            type=int,
                            default=None,
                            metavar='<max-nodes>',
                            help='The nodegroup maximum node count.')
        parser.add_argument('--role',
                            dest='role',
                            type=str,
                            default='worker',
                            metavar='<role>',
                            help=('The role of the nodegroup'))
        parser.add_argument(
            '--image',
            metavar='<image>',
            help=_('The name or UUID of the base image to customize for the '
                   'NodeGroup.'))
        parser.add_argument(
            '--flavor',
            metavar='<flavor>',
            help=_('The nova flavor name or UUID to use when launching the '
                   'nodes in this NodeGroup.'))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        args = {
            'name': parsed_args.name,
            'node_count': parsed_args.node_count,
            'max_node_count': parsed_args.max_node_count,
            'min_node_count': parsed_args.min_node_count,
            'role': parsed_args.role,
        }

        if parsed_args.labels is not None:
            args['labels'] = magnum_utils.handle_labels(parsed_args.labels)

        if parsed_args.docker_volume_size is not None:
            args['docker_volume_size'] = parsed_args.docker_volume_size

        if parsed_args.flavor is not None:
            args['flavor_id'] = parsed_args.flavor

        if parsed_args.image is not None:
            args['image_id'] = parsed_args.image

        cluster_id = parsed_args.cluster
        nodegroup = mag_client.nodegroups.create(cluster_id, **args)
        print("Request to create nodegroup %s accepted"
              % nodegroup.uuid)


class DeleteNodeGroup(command.Command):
    _description = _("Delete a nodegroup")

    def get_parser(self, prog_name):
        parser = super(DeleteNodeGroup, self).get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('ID or name of the cluster where the nodegroup(s) '
                   'belong(s).'))
        parser.add_argument(
            'nodegroup',
            nargs='+',
            metavar='<nodegroup>',
            help='ID or name of the nodegroup(s) to delete.')

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        cluster_id = parsed_args.cluster
        for ng in parsed_args.nodegroup:
            mag_client.nodegroups.delete(cluster_id, ng)
            print("Request to delete nodegroup %s has been accepted." % ng)


class ListNodeGroup(command.Lister):
    _description = _("List nodegroups")

    def get_parser(self, prog_name):
        parser = super(ListNodeGroup, self).get_parser(prog_name)

        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('ID or name of the cluster where the nodegroup belongs.'))
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of nodegroups to return'))
        parser.add_argument(
            '--sort-key',
            metavar='<sort-key>',
            help=_('Column to sort results by'))
        parser.add_argument(
            '--sort-dir',
            metavar='<sort-dir>',
            choices=['desc', 'asc'],
            help=_('Direction to sort. "asc" or "desc".'))
        parser.add_argument(
            '--role',
            metavar='<role>',
            help=_('List the nodegroups in the cluster with this role'))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        columns = ['uuid', 'name', 'flavor_id', 'image_id', 'node_count',
                   'status', 'role']
        cluster_id = parsed_args.cluster
        nodegroups = mag_client.nodegroups.list(cluster_id,
                                                limit=parsed_args.limit,
                                                sort_key=parsed_args.sort_key,
                                                sort_dir=parsed_args.sort_dir,
                                                role=parsed_args.role)
        return (
            columns,
            (utils.get_item_properties(n, columns) for n in nodegroups)
        )


class ShowNodeGroup(command.ShowOne):
    _description = _("Show a nodegroup")

    def get_parser(self, prog_name):
        parser = super(ShowNodeGroup, self).get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('ID or name of the cluster where the nodegroup belongs.'))
        parser.add_argument(
            'nodegroup',
            metavar='<nodegroup>',
            help=_('ID or name of the nodegroup to show.')
            )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        columns = NODEGROUP_ATTRIBUTES

        mag_client = self.app.client_manager.container_infra
        cluster_id = parsed_args.cluster
        nodegroup = mag_client.nodegroups.get(cluster_id,
                                              parsed_args.nodegroup)

        return (columns, utils.get_item_properties(nodegroup, columns))


class UpdateNodeGroup(command.Command):
    _description = _("Update a Nodegroup")

    def get_parser(self, prog_name):
        parser = super(UpdateNodeGroup, self).get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('ID or name of the cluster where the nodegroup belongs.'))
        parser.add_argument(
            'nodegroup',
            metavar='<nodegroup>',
            help=_('The name or UUID of cluster to update'))

        parser.add_argument(
            'op',
            metavar='<op>',
            choices=['add', 'replace', 'remove'],
            help=_("Operations: one of 'add', 'replace' or 'remove'"))

        parser.add_argument(
            'attributes',
            metavar='<path=value>',
            nargs='+',
            action='append',
            default=[],
            help=_(
                "Attributes to add/replace or remove (only PATH is necessary "
                "on remove)"))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra

        patch = magnum_utils.args_array_to_patch(parsed_args.op,
                                                 parsed_args.attributes[0])

        cluster_id = parsed_args.cluster
        mag_client.nodegroups.update(cluster_id, parsed_args.nodegroup,
                                     patch)
        print("Request to update nodegroup %s has been accepted." %
              parsed_args.nodegroup)
