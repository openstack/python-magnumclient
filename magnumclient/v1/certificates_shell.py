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

import os.path

from magnumclient.common import cliutils as utils


def _show_cert(certificate):
    print(certificate.pem)


@utils.arg('--bay',
           required=True,
           metavar='<bay>',
           help='ID or name of the bay.')
def do_ca_show(cs, args):
    """Show details about the CA certificate for a bay."""
    bay = cs.bays.get(args.bay)
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
    """Generate the CA certificate for a bay."""
    bay = cs.bays.get(args.bay)
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
