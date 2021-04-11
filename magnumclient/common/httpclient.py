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

import copy
from http import client as http_client
import io
import logging
import os
import socket
import ssl
from urllib import parse as urlparse

from keystoneauth1 import adapter
from oslo_serialization import jsonutils
from oslo_utils import importutils

from magnumclient import exceptions

osprofiler_web = importutils.try_import("osprofiler.web")

LOG = logging.getLogger(__name__)
USER_AGENT = 'python-magnumclient'
CHUNKSIZE = 1024 * 64  # 64kB

API_VERSION = '/v1'
DEFAULT_API_VERSION = 'latest'


def _extract_error_json_text(body_json):
    error_json = {}
    if 'error_message' in body_json:
        raw_msg = body_json['error_message']
        error_json = jsonutils.loads(raw_msg)
    elif 'error' in body_json:
        error_body = body_json['error']
        error_json = {'faultstring': error_body['title'],
                      'debuginfo': error_body['message']}
    else:
        error_body = body_json['errors'][0]
        error_json = {'faultstring': error_body['title']}
        if 'detail' in error_body:
            error_json['debuginfo'] = error_body['detail']
        elif 'description' in error_body:
            error_json['debuginfo'] = error_body['description']
    return error_json


def _extract_error_json(body, resp):
    """Return error_message from the HTTP response body."""
    try:
        content_type = resp.headers.get("Content-Type", "")
    except AttributeError:
        content_type = ""
    if content_type.startswith("application/json"):
        try:
            body_json = resp.json()
            return _extract_error_json_text(body_json)
        except AttributeError:
            body_json = jsonutils.loads(body)
            return _extract_error_json_text(body_json)
        except ValueError:
            return {}
    else:
        try:
            body_json = jsonutils.loads(body)
            return _extract_error_json_text(body_json)
        except ValueError:
            return {}


class HTTPClient(object):

    def __init__(self, endpoint, api_version=DEFAULT_API_VERSION, **kwargs):
        self.endpoint = endpoint
        self.auth_token = kwargs.get('token')
        self.auth_ref = kwargs.get('auth_ref')
        self.api_version = api_version
        self.connection_params = self.get_connection_params(endpoint, **kwargs)

    @staticmethod
    def get_connection_params(endpoint, **kwargs):
        parts = urlparse.urlparse(endpoint)

        # trim API version and trailing slash from endpoint
        path = parts.path
        path = path.rstrip('/').rstrip(API_VERSION)

        _args = (parts.hostname, parts.port, path)
        _kwargs = {'timeout': (float(kwargs.get('timeout'))
                               if kwargs.get('timeout') else 600)}

        if parts.scheme == 'https':
            _class = VerifiedHTTPSConnection
            _kwargs['ca_file'] = kwargs.get('ca_file', None)
            _kwargs['cert_file'] = kwargs.get('cert_file', None)
            _kwargs['key_file'] = kwargs.get('key_file', None)
            _kwargs['insecure'] = kwargs.get('insecure', False)
        elif parts.scheme == 'http':
            _class = http_client.HTTPConnection
        else:
            msg = 'Unsupported scheme: %s' % parts.scheme
            raise exceptions.EndpointException(msg)

        return (_class, _args, _kwargs)

    def get_connection(self):
        _class = self.connection_params[0]
        return _class(*self.connection_params[1][0:2],
                      **self.connection_params[2])

    def log_curl_request(self, method, url, kwargs):
        curl = ['curl -i -X %s' % method]

        for (key, value) in kwargs['headers'].items():
            header = '-H \'%s: %s\'' % (key, value)
            curl.append(header)

        conn_params_fmt = [
            ('key_file', '--key %s'),
            ('cert_file', '--cert %s'),
            ('ca_file', '--cacert %s'),
        ]
        for (key, fmt) in conn_params_fmt:
            value = self.connection_params[2].get(key)
            if value:
                curl.append(fmt % value)

        if self.connection_params[2].get('insecure'):
            curl.append('-k')

        if 'body' in kwargs:
            curl.append('-d \'%s\'' % kwargs['body'])

        curl.append('%s/%s' % (self.endpoint, url.lstrip(API_VERSION)))
        LOG.debug(' '.join(curl))

    @staticmethod
    def log_http_response(resp, body=None):
        status = (resp.version / 10.0, resp.status, resp.reason)
        dump = ['\nHTTP/%.1f %s %s' % status]
        dump.extend(['%s: %s' % (k, v) for k, v in resp.getheaders()])
        dump.append('')
        if body:
            dump.extend([body, ''])
        LOG.debug('\n'.join(dump))

    def _make_connection_url(self, url):
        (_class, _args, _kwargs) = self.connection_params
        base_url = _args[2]
        return '%s/%s' % (base_url, url.lstrip('/'))

    def _http_request(self, url, method, **kwargs):
        """Send an http request with the specified characteristics.

        Wrapper around httplib.HTTP(S)Connection.request to handle tasks such
        as setting headers and error handling.
        """
        # Copy the kwargs so we can reuse the original in case of redirects
        kwargs['headers'] = copy.deepcopy(kwargs.get('headers', {}))
        kwargs['headers'].setdefault('User-Agent', USER_AGENT)
        if self.api_version:
            version_string = 'container-infra %s' % self.api_version
            kwargs['headers'].setdefault(
                'OpenStack-API-Version', version_string)
        if self.auth_token:
            kwargs['headers'].setdefault('X-Auth-Token', self.auth_token)

        self.log_curl_request(method, url, kwargs)
        conn = self.get_connection()

        try:
            conn_url = self._make_connection_url(url)
            conn.request(method, conn_url, **kwargs)
            resp = conn.getresponse()
        except socket.gaierror as e:
            message = ("Error finding address for %(url)s: %(e)s"
                       % dict(url=url, e=e))
            raise exceptions.EndpointNotFound(message)
        except (socket.error, socket.timeout) as e:
            endpoint = self.endpoint
            message = ("Error communicating with %(endpoint)s %(e)s"
                       % dict(endpoint=endpoint, e=e))
            raise exceptions.ConnectionRefused(message)

        body_iter = ResponseBodyIterator(resp)

        # Read body into string if it isn't obviously image data
        body_str = None
        if resp.getheader('content-type', None) != 'application/octet-stream':
            # decoding byte to string is necessary for Python 3.4 compatibility
            # this issues has not been found with Python 3.4 unit tests
            # because the test creates a fake http response of type str
            # the if statement satisfies test (str) and real (bytes) behavior
            body_list = [
                chunk.decode("utf-8") if isinstance(chunk, bytes)
                else chunk for chunk in body_iter
            ]
            body_str = ''.join(body_list)
            self.log_http_response(resp, body_str)
            body_iter = io.StringIO(body_str)
        else:
            self.log_http_response(resp)

        if 400 <= resp.status < 600:
            LOG.warning("Request returned failure status.")
            error_json = _extract_error_json(body_str, resp)
            raise exceptions.from_response(
                resp, error_json.get('faultstring'),
                error_json.get('debuginfo'), method, url)
        elif resp.status in (301, 302, 305):
            # Redirected. Reissue the request to the new location.
            return self._http_request(resp['location'], method, **kwargs)
        elif resp.status == 300:
            raise exceptions.from_response(resp, method=method, url=url)

        return resp, body_iter

    def json_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type', 'application/json')
        kwargs['headers'].setdefault('Accept', 'application/json')

        if 'body' in kwargs:
            kwargs['body'] = jsonutils.dumps(kwargs['body'])

        resp, body_iter = self._http_request(url, method, **kwargs)
        content_type = resp.getheader('content-type', None)

        if resp.status == 204 or resp.status == 205 or content_type is None:
            return resp, list()

        if 'application/json' in content_type:
            body = ''.join([chunk for chunk in body_iter])
            try:
                body = jsonutils.loads(body)
            except ValueError:
                LOG.error('Could not decode response body as JSON')
        else:
            body = None

        return resp, body

    def raw_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type',
                                     'application/octet-stream')
        return self._http_request(url, method, **kwargs)


class VerifiedHTTPSConnection(http_client.HTTPSConnection):
    """httplib-compatibile connection using client-side SSL authentication

    :see http://code.activestate.com/recipes/
            577548-https-httplib-client-connection-with-certificate-v/
    """

    def __init__(self, host, port, key_file=None, cert_file=None,
                 ca_file=None, timeout=None, insecure=False):
        http_client.HTTPSConnection.__init__(self, host, port,
                                             key_file=key_file,
                                             cert_file=cert_file)
        self.key_file = key_file
        self.cert_file = cert_file
        if ca_file is not None:
            self.ca_file = ca_file
        else:
            self.ca_file = self.get_system_ca_file()
        self.timeout = timeout
        self.insecure = insecure

    def connect(self):
        """Connect to a host on a given (SSL) port.

        If ca_file is pointing somewhere, use it to check Server Certificate.

        Redefined/copied and extended from httplib.py:1105 (Python 2.6.x).
        This is needed to pass cert_reqs=ssl.CERT_REQUIRED as parameter to
        ssl.wrap_socket(), which forces SSL to check server certificate against
        our client certificate.
        """
        sock = socket.create_connection((self.host, self.port), self.timeout)

        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        if self.insecure is True:
            kwargs = {'cert_reqs': ssl.CERT_NONE}
        else:
            kwargs = {'cert_reqs': ssl.CERT_REQUIRED, 'ca_certs': self.ca_file}

        if self.cert_file:
            kwargs['certfile'] = self.cert_file
            if self.key_file:
                kwargs['keyfile'] = self.key_file

        self.sock = ssl.wrap_socket(sock, **kwargs)

    @staticmethod
    def get_system_ca_file():
        """Return path to system default CA file."""
        # Standard CA file locations for Debian/Ubuntu, RedHat/Fedora,
        # Suse, FreeBSD/OpenBSD
        ca_path = ['/etc/ssl/certs/ca-certificates.crt',
                   '/etc/pki/tls/certs/ca-bundle.crt',
                   '/etc/ssl/ca-bundle.pem',
                   '/etc/ssl/cert.pem']
        for ca in ca_path:
            if os.path.exists(ca):
                return ca
        return None


class SessionClient(adapter.LegacyJsonAdapter):
    """HTTP client based on Keystone client session."""

    def __init__(self, user_agent=USER_AGENT, logger=LOG,
                 api_version=DEFAULT_API_VERSION, *args, **kwargs):
        self.user_agent = USER_AGENT
        self.api_version = api_version
        super(SessionClient, self).__init__(*args, **kwargs)

    def _http_request(self, url, method, **kwargs):
        if url.startswith(API_VERSION):
            url = url[len(API_VERSION):]

        kwargs.setdefault('user_agent', self.user_agent)
        kwargs.setdefault('auth', self.auth)
        kwargs.setdefault('endpoint_override', self.endpoint_override)

        # Copy the kwargs so we can reuse the original in case of redirects
        kwargs['headers'] = copy.deepcopy(kwargs.get('headers', {}))
        kwargs['headers'].setdefault('User-Agent', self.user_agent)
        # NOTE(tovin07): osprofiler_web.get_trace_id_headers does not add any
        # headers in case if osprofiler is not initialized.
        if osprofiler_web:
            kwargs['headers'].update(osprofiler_web.get_trace_id_headers())
        if self.api_version:
            version_string = 'container-infra %s' % self.api_version
            kwargs['headers'].setdefault(
                'OpenStack-API-Version', version_string)

        endpoint_filter = kwargs.setdefault('endpoint_filter', {})
        endpoint_filter.setdefault('interface', self.interface)
        endpoint_filter.setdefault('service_type', self.service_type)
        endpoint_filter.setdefault('region_name', self.region_name)

        resp = self.session.request(url, method,
                                    raise_exc=False, **kwargs)

        if 400 <= resp.status_code < 600:
            error_json = _extract_error_json(resp.content, resp)
            raise exceptions.from_response(
                resp, error_json.get('faultstring'),
                error_json.get('debuginfo'), method, url)
        elif resp.status_code in (301, 302, 305):
            # Redirected. Reissue the request to the new location.
            location = resp.headers.get('location')
            resp = self._http_request(location, method, **kwargs)
        elif resp.status_code == 300:
            raise exceptions.from_response(resp, method=method, url=url)
        return resp

    def json_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type', 'application/json')
        kwargs['headers'].setdefault('Accept', 'application/json')
        if 'body' in kwargs:
            kwargs['data'] = jsonutils.dumps(kwargs.pop('body'))

        resp = self._http_request(url, method, **kwargs)
        body = resp.content
        content_type = resp.headers.get('content-type', None)
        status = resp.status_code
        if status == 204 or status == 205 or content_type is None:
            return resp, list()
        if 'application/json' in content_type:
            try:
                body = resp.json()
            except ValueError:
                LOG.error('Could not decode response body as JSON')
        else:
            body = None

        return resp, body

    def raw_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type',
                                     'application/octet-stream')
        resp = self._http_request(url, method, **kwargs)
        body = resp.content
        status = resp.status_code
        content_type = resp.headers.get('content-type', None)

        if status == 204 or status == 205 or content_type is None:
            return resp, list()
        if 'application/json' in content_type:
            try:
                body = resp.json()
            except ValueError:
                LOG.error('Could not decode response body as JSON')
        else:
            body = None

        return resp, body


class ResponseBodyIterator(object):
    """A class that acts as an iterator over an HTTP response."""

    def __init__(self, resp):
        self.resp = resp

    def __iter__(self):
        while True:
            try:
                yield self.next()
            except StopIteration:
                return

    def __bool__(self):
        return hasattr(self, 'items')

    __nonzero__ = __bool__  # Python 2.x compatibility

    def next(self):
        chunk = self.resp.read(CHUNKSIZE)
        if chunk:
            return chunk
        else:
            raise StopIteration


def _construct_http_client(*args, **kwargs):
    session = kwargs.pop('session', None)
    auth = kwargs.pop('auth', None)

    if session:
        service_type = kwargs.pop('service_type', 'baremetal')
        interface = kwargs.pop('endpoint_type', None)
        region_name = kwargs.pop('region_name', None)
        return SessionClient(session=session,
                             auth=auth,
                             interface=interface,
                             service_type=service_type,
                             region_name=region_name,
                             service_name=None,
                             user_agent='python-magnumclient')
    else:
        return HTTPClient(*args, **kwargs)
