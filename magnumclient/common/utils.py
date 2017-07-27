# -*- coding: utf-8 -*-
#
# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
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

import json
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID

from magnumclient import exceptions as exc
from magnumclient.i18n import _


def common_filters(marker=None, limit=None, sort_key=None, sort_dir=None):
    """Generate common filters for any list request.

    :param marker: entity ID from which to start returning entities.
    :param limit: maximum number of entities to return.
    :param sort_key: field to use for sorting.
    :param sort_dir: direction of sorting: 'asc' or 'desc'.
    :returns: list of string filters.
    """
    filters = []
    if isinstance(limit, int):
        filters.append('limit=%s' % limit)
    if marker is not None:
        filters.append('marker=%s' % marker)
    if sort_key is not None:
        filters.append('sort_key=%s' % sort_key)
    if sort_dir is not None:
        filters.append('sort_dir=%s' % sort_dir)
    return filters


def split_and_deserialize(string):
    """Split and try to JSON deserialize a string.

    Gets a string with the KEY=VALUE format, split it (using '=' as the
    separator) and try to JSON deserialize the VALUE.
    :returns: A tuple of (key, value).
    """
    try:
        key, value = string.split("=", 1)
    except ValueError:
        raise exc.CommandError(_('Attributes must be a list of '
                                 'PATH=VALUE not "%s"') % string)
    try:
        value = json.loads(value)
    except ValueError:
        pass

    return (key, value)


def args_array_to_patch(op, attributes):
    patch = []
    for attr in attributes:
        # Sanitize
        if not attr.startswith('/'):
            attr = '/' + attr
        if op in ['add', 'replace']:
            path, value = split_and_deserialize(attr)
            patch.append({'op': op, 'path': path, 'value': value})

        elif op == "remove":
            # For remove only the key is needed
            patch.append({'op': op, 'path': attr})
        else:
            raise exc.CommandError(_('Unknown PATCH operation: %s') % op)
    return patch


def handle_labels(labels):
    labels = format_labels(labels)
    if 'mesos_slave_executor_env_file' in labels:
        environment_variables_data = handle_json_from_file(
            labels['mesos_slave_executor_env_file'])
        labels['mesos_slave_executor_env_variables'] = json.dumps(
            environment_variables_data)
    return labels


def format_labels(lbls, parse_comma=True):
    '''Reformat labels into dict of format expected by the API.'''

    if not lbls:
        return {}

    if parse_comma:
        # expect multiple invocations of --labels but fall back
        # to either , or ; delimited if only one --labels is specified
        if len(lbls) == 1 and lbls[0].count('=') > 1:
            lbls = lbls[0].replace(';', ',').split(',')

    labels = {}
    for l in lbls:
        try:
            (k, v) = l.split(('='), 1)
        except ValueError:
            raise exc.CommandError(_('labels must be a list of KEY=VALUE '
                                     'not %s') % l)
        if k not in labels:
            labels[k] = v
        else:
            labels[k] += ",%s" % v

    return labels


def print_list_field(field):
    return lambda obj: ', '.join(getattr(obj, field))


def handle_json_from_file(json_arg):
    """Attempts to read JSON file by the file url.

    :param json_arg: May be a file name containing the JSON.
    :returns: A list or dictionary parsed from JSON.
    """

    try:
        with open(json_arg, 'r') as f:
            json_arg = f.read().strip()
            json_arg = json.loads(json_arg)
    except IOError as e:
        err = _("Cannot get JSON from file '%(file)s'. "
                "Error: %(err)s") % {'err': e, 'file': json_arg}
        raise exc.InvalidAttribute(err)
    except ValueError as e:
        err = (_("For JSON: '%(string)s', error: '%(err)s'") %
               {'err': e, 'string': json_arg})
        raise exc.InvalidAttribute(err)

    return json_arg


def config_cluster(cluster, cluster_template, cfg_dir, force=False):
    """Return and write configuration for the given cluster."""
    if cluster_template.coe == 'kubernetes':
        return _config_cluster_kubernetes(cluster, cluster_template,
                                          cfg_dir, force)
    elif (cluster_template.coe == 'swarm'
          or cluster_template.coe == 'swarm-mode'):
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
               "  name: %(name)s\n"
               "current-context: %(name)s\n"
               "kind: Config\n"
               "preferences: {}\n"
               "users:\n"
               "- name: %(name)s'\n"
               % {'name': cluster.name, 'api_address': cluster.api_address})
    else:
        cfg = ("apiVersion: v1\n"
               "clusters:\n"
               "- cluster:\n"
               "    certificate-authority: %(cfg_dir)s/ca.pem\n"
               "    server: %(api_address)s\n"
               "  name: %(name)s\n"
               "contexts:\n"
               "- context:\n"
               "    cluster: %(name)s\n"
               "    user: %(name)s\n"
               "  name: %(name)s\n"
               "current-context: %(name)s\n"
               "kind: Config\n"
               "preferences: {}\n"
               "users:\n"
               "- name: %(name)s\n"
               "  user:\n"
               "    client-certificate: %(cfg_dir)s/cert.pem\n"
               "    client-key: %(cfg_dir)s/key.pem\n"
               % {'name': cluster.name,
                  'api_address': cluster.api_address,
                  'cfg_dir': cfg_dir})

    if os.path.exists(cfg_file) and not force:
        raise exc.CommandError("File %s exists, aborting." % cfg_file)
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


def generate_csr_and_key():
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
