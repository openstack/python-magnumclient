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

from magnumclient.common import cliutils as utils
from magnumclient.i18n import _

from osc_lib.command import command


class ListStats(command.Command):
    _description = _("Show stats for the given project_id")

    def get_parser(self, prog_name):
        parser = super(ListStats, self).get_parser(prog_name)
        parser.add_argument('project_id',
                            metavar='<project>',
                            help='Project ID')
        return parser

    def take_action(self, parsed_args):
        mag_client = self.app.client_manager.container_infra
        opts = {
            'project_id': parsed_args.project_id
        }

        stats = mag_client.stats.list(**opts)
        try:
            utils.print_dict(stats._info)
        except AttributeError:
            return None
