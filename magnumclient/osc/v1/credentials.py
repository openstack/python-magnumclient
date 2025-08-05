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

from osc_lib.command import command
from osc_lib.i18n import _


class RotateCredential(command.Command):
    _description = _("Rotate the credentials for the cluster using the "
                     "current user account.")

    def get_parser(self, prog_name):
        parser = super(RotateCredential, self).get_parser(prog_name)
        parser.add_argument('cluster',
                            metavar='<cluster>',
                            help='ID or name of the cluster')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra

        try:
            cluster = mag_client.credentials.update(parsed_args.cluster)
        except Exception as e:
            print("Credential rotation failed: %s" % e)
        else:
            print("Request to rotate credentials for cluster %s accepted."
                  % cluster.uuid)
