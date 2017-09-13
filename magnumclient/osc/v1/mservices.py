# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from osc_lib.command import command
from osc_lib import utils


def _get_client(obj, parsed_args):
    obj.log.debug("take_action(%s)" % parsed_args)
    return obj.app.client_manager.container_infra


class ListService(command.Lister):
    """Print a list of Magnum services."""

    log = logging.getLogger(__name__ + ".ListService")

    def get_parser(self, prog_name):
        parser = super(ListService, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        client = _get_client(self, parsed_args)
        services = client.mservices.list()
        columns = ('id', 'host', 'binary', 'state', 'disabled',
                   'disabled_reason', 'created_at', 'updated_at')
        return (columns, (utils.get_item_properties(service, columns)
                          for service in services))
