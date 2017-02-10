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
from oslo_log import log as logging


class ListTemplateCluster(command.Lister):
    """List Cluster Templates."""

    log = logging.getLogger(__name__ + ".ListTemplateCluster")

    def get_parser(self, prog_name):
        parser = super(ListTemplateCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of cluster templates to return'))
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
            '--fields',
            default=None,
            metavar='<fields>',
            help=_('Comma-separated list of fields to display. '
                   'Available fields: uuid, name, coe, image_id, public, '
                   'link, apiserver_port, server_type, tls_disabled, '
                   'registry_enabled'
                   )
            )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        columns = ['uuid', 'name']
        cts = mag_client.cluster_templates.list()
        return (
            columns,
            (utils.get_item_properties(ct, columns) for ct in cts)
        )
