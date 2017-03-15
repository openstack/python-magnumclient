# Copyright 2016 EasyStack.  All rights reserved.
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


class CreateCluster(command.Command):
    _description = _("Create a cluster")

    def get_parser(self, prog_name):
        parser = super(CreateCluster, self).get_parser(prog_name)
        # NOTE: All arguments are positional and, if not provided
        # with a default, required.
        parser.add_argument('--cluster-template',
                            dest='cluster_template',
                            required=True,
                            metavar='<cluster-template>',
                            help='ID or name of the cluster template.')
        parser.add_argument('--discovery-url',
                            dest='discovery_url',
                            metavar='<discovery-url>',
                            help=('Specifies custom delivery url for '
                                  'node discovery.'))
        parser.add_argument('--docker-volume-size',
                            dest='docker_volume_size',
                            type=int,
                            metavar='<docker-volume-size>',
                            help=('The size in GB for the docker volume to '
                                  'use.'))
        parser.add_argument('--keypair',
                            default=None,
                            metavar='<keypair>',
                            help='UUID or name of the keypair to use.')
        parser.add_argument('--master-count',
                            dest='master_count',
                            type=int,
                            default=1,
                            metavar='<master-count>',
                            help='The number of master nodes for the cluster.')
        parser.add_argument('--name',
                            metavar='<name>',
                            help='Name of the cluster to create.')
        parser.add_argument('--node-count',
                            dest='node_count',
                            type=int,
                            default=1,
                            metavar='<node-count>',
                            help='The cluster node count.')
        parser.add_argument('--timeout',
                            type=int,
                            default=60,
                            metavar='<timeout>',
                            help=('The timeout for cluster creation time. The '
                                  'default is 60 minutes.'))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        args = {
            'cluster_template_id': parsed_args.cluster_template,
            'create_timeout': parsed_args.timeout,
            'discovery_url': parsed_args.discovery_url,
            'docker_volume_size': parsed_args.docker_volume_size,
            'keypair': parsed_args.keypair,
            'master_count': parsed_args.master_count,
            'name': parsed_args.name,
            'node_count': parsed_args.node_count,
        }
        cluster = mag_client.clusters.create(**args)
        print("Request to create cluster %s accepted"
              % cluster.uuid)


class ListCluster(command.Lister):
    _description = _("List clusters")

    def get_parser(self, prog_name):
        parser = super(ListCluster, self).get_parser(prog_name)

        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of clusters to return'))
        parser.add_argument(
            '--sort-key',
            metavar='<sort-key>',
            help=_('Column to sort results by'))
        parser.add_argument(
            '--sort-dir',
            metavar='<sort-dir>',
            choices=['desc', 'asc'],
            help=_('Direction to sort. "asc" or "desc".'))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        columns = [
            'uuid', 'name', 'keypair', 'node_count', 'master_count', 'status']
        clusters = mag_client.clusters.list(limit=parsed_args.limit,
                                            sort_key=parsed_args.sort_key,
                                            sort_dir=parsed_args.sort_dir)
        return (
            columns,
            (utils.get_item_properties(c, columns) for c in clusters)
        )
