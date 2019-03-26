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
    'is_default'
]


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
        columns = ['uuid', 'name', 'flavor_id', 'node_count', 'role']
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
