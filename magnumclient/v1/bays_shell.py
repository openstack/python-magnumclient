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
from magnumclient.common import utils as magnum_utils
from magnumclient import exceptions
from magnumclient.i18n import _

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
import os


DEPRECATION_MESSAGE = (
    'WARNING: Bay commands are deprecated and will be removed in a future '
    'release.\nUse cluster commands to avoid seeing this message.')


def _show_bay(bay):
    del bay._info['links']
    utils.print_dict(bay._info)


@utils.arg('--marker',
           metavar='<marker>',
           default=None,
           help=_('The last bay UUID of the previous page; '
                  'displays list of bays after "marker".'))
@utils.arg('--limit',
           metavar='<limit>',
           type=int,
           help=_('Maximum number of bays to return.'))
@utils.arg('--sort-key',
           metavar='<sort-key>',
           help=_('Column to sort results by.'))
@utils.arg('--sort-dir',
           metavar='<sort-dir>',
           choices=['desc', 'asc'],
           help=_('Direction to sort. "asc" or "desc".'))
@utils.arg('--fields',
           default=None,
           metavar='<fields>',
           help=_('Comma-separated list of fields to display. '
                  'Available fields: uuid, name, baymodel_id, stack_id, '
                  'status, master_count, node_count, links, bay_create_timeout'
                  )
           )
@utils.deprecated(DEPRECATION_MESSAGE)
def do_bay_list(cs, args):
    """Print a list of available bays.

    (Deprecated in favor of cluster-list.)
    """
    bays = cs.bays.list(marker=args.marker, limit=args.limit,
                        sort_key=args.sort_key,
                        sort_dir=args.sort_dir)
    columns = ['uuid', 'name', 'node_count', 'master_count', 'status']
    columns += utils._get_list_table_columns_and_formatters(
        args.fields, bays,
        exclude_fields=(c.lower() for c in columns))[0]
    utils.print_list(bays, columns,
                     {'versions': magnum_utils.print_list_field('versions')},
                     sortby_index=None)


@utils.deprecated(DEPRECATION_MESSAGE)
@utils.arg('--name',
           metavar='<name>',
           help=_('Name of the bay to create.'))
@utils.arg('--baymodel',
           required=True,
           metavar='<baymodel>',
           help=_('ID or name of the baymodel.'))
@utils.arg('--node-count',
           metavar='<node-count>',
           type=int,
           default=1,
           help=_('The bay node count.'))
@utils.arg('--master-count',
           metavar='<master-count>',
           type=int,
           default=1,
           help=_('The number of master nodes for the bay.'))
@utils.arg('--discovery-url',
           metavar='<discovery-url>',
           help=_('Specifies custom discovery url for node discovery.'))
@utils.arg('--timeout',
           metavar='<timeout>',
           type=int,
           default=60,
           help=_('The timeout for bay creation in minutes. The default '
                  'is 60 minutes.'))
def do_bay_create(cs, args):
    """Create a bay.

    (Deprecated in favor of cluster-create.)
    """
    baymodel = cs.baymodels.get(args.baymodel)

    opts = {}
    opts['name'] = args.name
    opts['baymodel_id'] = baymodel.uuid
    opts['node_count'] = args.node_count
    opts['master_count'] = args.master_count
    opts['discovery_url'] = args.discovery_url
    opts['bay_create_timeout'] = args.timeout
    try:
        bay = cs.bays.create(**opts)
        # support for non-async in 1.1
        if args.magnum_api_version and args.magnum_api_version == '1.1':
            _show_bay(bay)
        else:
            uuid = str(bay._info['uuid'])
            print("Request to create bay %s has been accepted." % uuid)
    except Exception as e:
        print("Create for bay %s failed: %s" %
              (opts['name'], e))


@utils.arg('bay',
           metavar='<bay>',
           nargs='+',
           help=_('ID or name of the (bay)s to delete.'))
@utils.deprecated(DEPRECATION_MESSAGE)
def do_bay_delete(cs, args):
    """Delete specified bay.

    (Deprecated in favor of cluster-delete.)
    """
    for id in args.bay:
        try:
            cs.bays.delete(id)
            print("Request to delete bay %s has been accepted." %
                  id)
        except Exception as e:
            print("Delete for bay %(bay)s failed: %(e)s" %
                  {'bay': id, 'e': e})


@utils.arg('bay',
           metavar='<bay>',
           help=_('ID or name of the bay to show.'))
@utils.arg('--long',
           action='store_true', default=False,
           help=_('Display extra associated Baymodel info.'))
@utils.deprecated(DEPRECATION_MESSAGE)
def do_bay_show(cs, args):
    """Show details about the given bay.

    (Deprecated in favor of cluster-show.)
    """
    bay = cs.bays.get(args.bay)
    if args.long:
        baymodel = cs.baymodels.get(bay.baymodel_id)
        del baymodel._info['links'], baymodel._info['uuid']

        for key in baymodel._info:
            if 'baymodel_' + key not in bay._info:
                bay._info['baymodel_' + key] = baymodel._info[key]
    _show_bay(bay)


@utils.arg('bay', metavar='<bay>', help=_("UUID or name of bay"))
@utils.arg('--rollback',
           action='store_true', default=False,
           help=_('Rollback bay on update failure.'))
@utils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help=_("Operations: 'add', 'replace' or 'remove'"))
@utils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help=_("Attributes to add/replace or remove "
           "(only PATH is necessary on remove)"))
@utils.deprecated(DEPRECATION_MESSAGE)
def do_bay_update(cs, args):
    """Update information about the given bay.

    (Deprecated in favor of cluster-update.)
    """
    if args.rollback and args.magnum_api_version and \
            args.magnum_api_version in ('1.0', '1.1', '1.2'):
        raise exceptions.CommandError(
            "Rollback is not supported in API v%s. "
            "Please use API v1.3+." % args.magnum_api_version)
    patch = magnum_utils.args_array_to_patch(args.op, args.attributes[0])
    bay = cs.bays.update(args.bay, patch, args.rollback)
    if args.magnum_api_version and args.magnum_api_version == '1.1':
        _show_bay(bay)
    else:
        print("Request to update bay %s has been accepted." % args.bay)


@utils.arg('bay',
           metavar='<bay>',
           help=_('ID or name of the bay to retrieve config.'))
@utils.arg('--dir',
           metavar='<dir>',
           default='.',
           help=_('Directory to save the certificate and config files.'))
@utils.arg('--force',
           action='store_true', default=False,
           help=_('Overwrite files if existing.'))
@utils.deprecated(DEPRECATION_MESSAGE)
def do_bay_config(cs, args):
    """Configure native client to access bay.

    You can source the output of this command to get the native client of the
    corresponding COE configured to access the bay.

    Example: eval $(magnum bay-config <bay-name>).

    (Deprecated in favor of cluster-config.)
    """
    args.dir = os.path.abspath(args.dir)
    bay = cs.bays.get(args.bay)
    if bay.status not in ('CREATE_COMPLETE', 'UPDATE_COMPLETE'):
        raise exceptions.CommandError("Bay in status %s" % bay.status)
    baymodel = cs.baymodels.get(bay.baymodel_id)
    opts = {
        'cluster_uuid': bay.uuid,
    }

    if not baymodel.tls_disabled:
        tls = _generate_csr_and_key()
        tls['ca'] = cs.certificates.get(**opts).pem
        opts['csr'] = tls['csr']
        tls['cert'] = cs.certificates.create(**opts).pem
        for k in ('key', 'cert', 'ca'):
            fname = "%s/%s.pem" % (args.dir, k)
            if os.path.exists(fname) and not args.force:
                raise Exception("File %s exists, aborting." % fname)
            else:
                f = open(fname, "w")
                f.write(tls[k])
                f.close()

    print(_config_bay(bay, baymodel, cfg_dir=args.dir, force=args.force))


def _config_bay(bay, baymodel, cfg_dir, force=False):
    """Return and write configuration for the given bay."""
    if baymodel.coe == 'kubernetes':
        return _config_bay_kubernetes(bay, baymodel, cfg_dir, force)
    elif baymodel.coe == 'swarm':
        return _config_bay_swarm(bay, baymodel, cfg_dir, force)


def _config_bay_kubernetes(bay, baymodel, cfg_dir, force=False):
    """Return and write configuration for the given kubernetes bay."""
    cfg_file = "%s/config" % cfg_dir
    if baymodel.tls_disabled:
        cfg = ("apiVersion: v1\n"
               "clusters:\n"
               "- cluster:\n"
               "    server: %(api_address)s\n"
               "  name: %(name)s\n"
               "contexts:\n"
               "- context:\n"
               "    cluster: %(name)s\n"
               "    user: %(name)s\n"
               "  name: default/%(name)s\n"
               "current-context: default/%(name)s\n"
               "kind: Config\n"
               "preferences: {}\n"
               "users:\n"
               "- name: %(name)s'\n"
               % {'name': bay.name, 'api_address': bay.api_address})
    else:
        cfg = ("apiVersion: v1\n"
               "clusters:\n"
               "- cluster:\n"
               "    certificate-authority: ca.pem\n"
               "    server: %(api_address)s\n"
               "  name: %(name)s\n"
               "contexts:\n"
               "- context:\n"
               "    cluster: %(name)s\n"
               "    user: %(name)s\n"
               "  name: default/%(name)s\n"
               "current-context: default/%(name)s\n"
               "kind: Config\n"
               "preferences: {}\n"
               "users:\n"
               "- name: %(name)s\n"
               "  user:\n"
               "    client-certificate: cert.pem\n"
               "    client-key: key.pem\n"
               % {'name': bay.name, 'api_address': bay.api_address})

    if os.path.exists(cfg_file) and not force:
        raise exceptions.CommandError("File %s exists, aborting." % cfg_file)
    else:
        f = open(cfg_file, "w")
        f.write(cfg)
        f.close()
    if 'csh' in os.environ['SHELL']:
        return "setenv KUBECONFIG %s\n" % cfg_file
    else:
        return "export KUBECONFIG=%s\n" % cfg_file


def _config_bay_swarm(bay, baymodel, cfg_dir, force=False):
    """Return and write configuration for the given swarm bay."""
    tls = "" if baymodel.tls_disabled else True
    if 'csh' in os.environ['SHELL']:
        result = ("setenv DOCKER_HOST %(docker_host)s\n"
                  "setenv DOCKER_CERT_PATH %(cfg_dir)s\n"
                  "setenv DOCKER_TLS_VERIFY %(tls)s\n"
                  % {'docker_host': bay.api_address,
                     'cfg_dir': cfg_dir,
                     'tls': tls}
                  )
    else:
        result = ("export DOCKER_HOST=%(docker_host)s\n"
                  "export DOCKER_CERT_PATH=%(cfg_dir)s\n"
                  "export DOCKER_TLS_VERIFY=%(tls)s\n"
                  % {'docker_host': bay.api_address,
                     'cfg_dir': cfg_dir,
                     'tls': tls}
                  )

    return result


def _generate_csr_and_key():
    """Return a dict with a new csr and key."""
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())

    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"Magnum User"),
    ])).sign(key, hashes.SHA256(), default_backend())

    result = {
        'csr': csr.public_bytes(
            encoding=serialization.Encoding.PEM).decode("utf-8"),
        'key': key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()).decode("utf-8"),
    }

    return result
