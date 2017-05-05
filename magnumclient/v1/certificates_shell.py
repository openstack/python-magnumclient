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
from magnumclient.i18n import _


DEPRECATION_MESSAGE = (
    'WARNING: The bay parameter is deprecated and will be removed in a future '
    'release.\nUse the cluster parameter to avoid seeing this message.')


def _show_cert(certificate):
    print(certificate.pem)


def _get_target_uuid(cs, args):
    target = None
    if args.cluster:
        target = cs.clusters.get(args.cluster)
    elif args.bay:
        print(DEPRECATION_MESSAGE)
        target = cs.bays.get(args.bay)
    else:
        raise utils.MissingArgs(['--cluster or --bay'])
    return target.uuid


@utils.arg('--bay',
           required=False,
           metavar='<bay>',
           help=_('ID or name of the bay.'))
@utils.arg('--cluster',
           required=False,
           metavar='<cluster>',
           help=_('ID or name of the cluster.'))
def do_ca_show(cs, args):
    """Show details about the CA certificate for a bay or cluster."""
    opts = {
        'cluster_uuid': _get_target_uuid(cs, args)
    }

    cert = cs.certificates.get(**opts)
    _show_cert(cert)


@utils.arg('--csr',
           metavar='<csr>',
           help=_('File path of the csr file to send to Magnum'
                  ' to get signed.'))
@utils.arg('--bay',
           required=False,
           metavar='<bay>',
           help=_('ID or name of the bay.'))
@utils.arg('--cluster',
           required=False,
           metavar='<cluster>',
           help=_('ID or name of the cluster.'))
def do_ca_sign(cs, args):
    """Generate the CA certificate for a bay or cluster."""
    opts = {
        'cluster_uuid': _get_target_uuid(cs, args)
    }

    if args.csr is None or not os.path.isfile(args.csr):
        print('A CSR must be provided.')
        return

    with open(args.csr, 'r') as f:
        opts['csr'] = f.read()

    cert = cs.certificates.create(**opts)
    _show_cert(cert)


@utils.arg('--cluster',
           required=True,
           metavar='<cluster>',
           help=_('ID or name of the cluster.'))
def do_ca_rotate(cs, args):
    """Rotate the CA certificate for a bay or cluster to revoke access."""
    cluster = cs.clusters.get(args.cluster)
    opts = {
        'cluster_uuid': cluster.uuid
    }

    cs.certificates.rotate_ca(**opts)
