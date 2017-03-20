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


# Maps old parameter names to their new names and whether they are required
# e.g. keypair-id to keypair
DEPRECATING_PARAMS = {
    "--keypair-id": "--keypair",
}


def _show_cluster(cluster):
    del cluster._info['links']
    utils.print_dict(cluster._info)


@utils.arg('--marker',
           metavar='<marker>',
           default=None,
           help=_('The last cluster UUID of the previous page; '
                  'displays list of clusters after "marker".'))
@utils.arg('--limit',
           metavar='<limit>',
           type=int,
           help=_('Maximum number of clusters to return.'))
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
                  'Available fields: uuid, name, cluster_template_id, '
                  'stack_id, status, master_count, node_count, links, '
                  'create_timeout'
                  )
           )
def do_cluster_list(cs, args):
    """Print a list of available clusters."""
    clusters = cs.clusters.list(marker=args.marker, limit=args.limit,
                                sort_key=args.sort_key,
                                sort_dir=args.sort_dir)
    columns = [
        'uuid', 'name', 'keypair', 'node_count', 'master_count', 'status'
    ]
    columns += utils._get_list_table_columns_and_formatters(
        args.fields, clusters,
        exclude_fields=(c.lower() for c in columns))[0]

    utils.print_list(clusters, columns,
                     {'versions': magnum_utils.print_list_field('versions')},
                     sortby_index=None)


@utils.deprecation_map(DEPRECATING_PARAMS)
@utils.arg('positional_name',
           metavar='<name>',
           nargs='?',
           default=None,
           help=_('Name of the cluster to create.'))
@utils.arg('--name',
           metavar='<name>',
           default=None,
           help=(_('Name of the cluster to create. %s') %
                 utils.NAME_DEPRECATION_HELP))
@utils.arg('--cluster-template',
           required=True,
           metavar='<cluster_template>',
           help=_('ID or name of the cluster template.'))
@utils.arg('--keypair-id',
           dest='keypair',
           metavar='<keypair>',
           default=None,
           help=utils.deprecation_message(
                'Name of the keypair to use for this cluster.',
                'keypair'))
@utils.arg('--keypair',
           dest='keypair',
           metavar='<keypair>',
           default=None,
           help=_('Name of the keypair to use for this cluster.'))
@utils.arg('--node-count',
           metavar='<node-count>',
           type=int,
           default=1,
           help=_('The cluster node count.'))
@utils.arg('--master-count',
           metavar='<master-count>',
           type=int,
           default=1,
           help=_('The number of master nodes for the cluster.'))
@utils.arg('--discovery-url',
           metavar='<discovery-url>',
           help=_('Specifies custom discovery url for node discovery.'))
@utils.arg('--timeout',
           metavar='<timeout>',
           type=int,
           default=60,
           help=_('The timeout for cluster creation in minutes. The default '
                  'is 60 minutes.'))
def do_cluster_create(cs, args):
    """Create a cluster."""
    args.command = 'cluster-create'

    utils.validate_name_args(args.positional_name, args.name)

    cluster_template = cs.cluster_templates.get(args.cluster_template)
    opts = dict()
    opts['name'] = args.positional_name or args.name
    opts['cluster_template_id'] = cluster_template.uuid
    opts['keypair'] = args.keypair
    opts['node_count'] = args.node_count
    opts['master_count'] = args.master_count
    opts['discovery_url'] = args.discovery_url
    opts['create_timeout'] = args.timeout

    try:
        cluster = cs.clusters.create(**opts)
        # support for non-async in 1.1
        if args.magnum_api_version and args.magnum_api_version == '1.1':
            _show_cluster(cluster)
        else:
            uuid = str(cluster._info['uuid'])
            print("Request to create cluster %s has been accepted." % uuid)
    except Exception as e:
        print("Create for cluster %s failed: %s" %
              (opts['name'], e))


@utils.arg('cluster',
           metavar='<cluster>',
           nargs='+',
           help=_('ID or name of the (cluster)s to delete.'))
def do_cluster_delete(cs, args):
    """Delete specified cluster."""
    for id in args.cluster:
        try:
            cs.clusters.delete(id)
            print("Request to delete cluster %s has been accepted." %
                  id)
        except Exception as e:
            print("Delete for cluster %(cluster)s failed: %(e)s" %
                  {'cluster': id, 'e': e})


@utils.arg('cluster',
           metavar='<cluster>',
           help=_('ID or name of the cluster to show.'))
@utils.arg('--long',
           action='store_true', default=False,
           help=_('Display extra associated cluster template info.'))
def do_cluster_show(cs, args):
    """Show details about the given cluster."""
    cluster = cs.clusters.get(args.cluster)
    if args.long:
        cluster_template = \
            cs.cluster_templates.get(cluster.cluster_template_id)
        del cluster_template._info['links'], cluster_template._info['uuid']

        for key in cluster_template._info:
            if 'clustertemplate_' + key not in cluster._info:
                cluster._info['clustertemplate_' + key] = \
                    cluster_template._info[key]
    _show_cluster(cluster)


@utils.arg('cluster', metavar='<cluster>', help=_("UUID or name of cluster"))
@utils.arg('--rollback',
           action='store_true', default=False,
           help=_('Rollback cluster on update failure.'))
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
def do_cluster_update(cs, args):
    """Update information about the given cluster."""
    if args.rollback and args.magnum_api_version and \
            args.magnum_api_version in ('1.0', '1.1', '1.2'):
        raise exceptions.CommandError(
            "Rollback is not supported in API v%s. "
            "Please use API v1.3+." % args.magnum_api_version)
    patch = magnum_utils.args_array_to_patch(args.op, args.attributes[0])
    try:
        cluster = cs.clusters.update(args.cluster, patch, args.rollback)
    except Exception as e:
        print("ERROR: %s" % e.details)
        return

    if args.magnum_api_version and args.magnum_api_version == '1.1':
        _show_cluster(cluster)
    else:
        print("Request to update cluster %s has been accepted." % args.cluster)


@utils.arg('cluster',
           metavar='<cluster>',
           help=_('ID or name of the cluster to retrieve config.'))
@utils.arg('--dir',
           metavar='<dir>',
           default='.',
           help=_('Directory to save the certificate and config files.'))
@utils.arg('--force',
           action='store_true', default=False,
           help=_('Overwrite files if existing.'))
def do_cluster_config(cs, args):
    """Configure native client to access cluster.

    You can source the output of this command to get the native client of the
    corresponding COE configured to access the cluster.

    Example: eval $(magnum cluster-config <cluster-name>).
    """
    args.dir = os.path.abspath(args.dir)
    cluster = cs.clusters.get(args.cluster)
    if cluster.status not in ('CREATE_COMPLETE', 'UPDATE_COMPLETE',
                              'ROLLBACK_COMPLETE'):
        raise exceptions.CommandError("cluster in status %s" % cluster.status)
    cluster_template = cs.cluster_templates.get(cluster.cluster_template_id)
    opts = {
        'cluster_uuid': cluster.uuid,
    }

    if not cluster_template.tls_disabled:
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

    print(_config_cluster(cluster, cluster_template,
                          cfg_dir=args.dir, force=args.force))


def _config_cluster(cluster, cluster_template, cfg_dir, force=False):
    """Return and write configuration for the given cluster."""
    if cluster_template.coe == 'kubernetes':
        return _config_cluster_kubernetes(cluster, cluster_template,
                                          cfg_dir, force)
    elif cluster_template.coe == 'swarm':
        return _config_cluster_swarm(cluster, cluster_template, cfg_dir, force)


def _config_cluster_kubernetes(cluster, cluster_template,
                               cfg_dir, force=False):
    """Return and write configuration for the given kubernetes cluster."""
    cfg_file = "%s/config" % cfg_dir
    if cluster_template.tls_disabled:
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
               % {'name': cluster.name, 'api_address': cluster.api_address})
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
               % {'name': cluster.name, 'api_address': cluster.api_address})

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


def _config_cluster_swarm(cluster, cluster_template, cfg_dir, force=False):
    """Return and write configuration for the given swarm cluster."""
    tls = "" if cluster_template.tls_disabled else True
    if 'csh' in os.environ['SHELL']:
        result = ("setenv DOCKER_HOST %(docker_host)s\n"
                  "setenv DOCKER_CERT_PATH %(cfg_dir)s\n"
                  "setenv DOCKER_TLS_VERIFY %(tls)s\n"
                  % {'docker_host': cluster.api_address,
                     'cfg_dir': cfg_dir,
                     'tls': tls}
                  )
    else:
        result = ("export DOCKER_HOST=%(docker_host)s\n"
                  "export DOCKER_CERT_PATH=%(cfg_dir)s\n"
                  "export DOCKER_TLS_VERIFY=%(tls)s\n"
                  % {'docker_host': cluster.api_address,
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
