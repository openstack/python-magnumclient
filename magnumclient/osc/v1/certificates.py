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

import os

from magnumclient.i18n import _

from osc_lib.command import command


def _show_cert(certificate):
    try:
        print(certificate.pem)
    except AttributeError:
        return None


def _get_target_uuid(cs, args):
    target = None
    if args.cluster:
        target = cs.clusters.get(args.cluster)
    return target.uuid


class RotateCa(command.Command):
    _description = _("Rotate the CA certificate for cluster to revoke access.")

    def get_parser(self, prog_name):
        parser = super(RotateCa, self).get_parser(prog_name)
        parser.add_argument('cluster',
                            metavar='<cluster>',
                            help='ID or name of the cluster')
        return parser

    def take_action(self, parsed_args):
        mag_client = self.app.client_manager.container_infra
        cluster = mag_client.clusters.get(parsed_args.cluster)
        opts = {
            'cluster_uuid': cluster.uuid
        }

        mag_client.certificates.rotate_ca(**opts)


class ShowCa(command.Command):
    _description = _("Show details about the CA certificate for a cluster.")

    def get_parser(self, prog_name):
        parser = super(ShowCa, self).get_parser(prog_name)
        # NOTE: All arguments are positional and, if not provided
        # with a default, required.
        parser.add_argument('cluster',
                            metavar='<cluster>',
                            help='ID or name of the cluster')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        cluster = mag_client.clusters.get(parsed_args.cluster)
        cert = mag_client.certificates.get(cluster.uuid)
        _show_cert(cert)


class SignCa(command.Command):
    _description = _("Generate the CA certificate for a cluster.")

    def get_parser(self, prog_name):
        parser = super(SignCa, self).get_parser(prog_name)
        # NOTE: All arguments are positional and, if not provided
        # with a default, required.
        parser.add_argument('cluster',
                            metavar='<cluster>',
                            help='ID or name of the cluster')
        parser.add_argument('csr',
                            metavar='<csr>',
                            help='File path of csr file to send to Magnum'
                                 ' to get signed.')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra

        opts = {
            'cluster_uuid': _get_target_uuid(mag_client, parsed_args)
        }

        if parsed_args.csr is None or not os.path.isfile(parsed_args.csr):
            print('A CSR must be provided.')
            return

        with open(parsed_args.csr, 'r') as f:
            opts['csr'] = f.read()

        cert = mag_client.certificates.create(**opts)
        _show_cert(cert)
