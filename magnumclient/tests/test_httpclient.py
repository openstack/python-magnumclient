# Copyright 2015 OpenStack LLC.
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

import mock
import six
import socket

from magnumclient.common.apiclient.exceptions import GatewayTimeout
from magnumclient.common.apiclient.exceptions import MultipleChoices
from magnumclient.common import httpclient as http
from magnumclient import exceptions as exc
from magnumclient.tests import utils

NORMAL_ERROR = 0
ERROR_DICT = 1
ERROR_LIST_WITH_DETAIL = 2
ERROR_LIST_WITH_DESC = 3


def _get_error_body(faultstring=None, debuginfo=None, err_type=NORMAL_ERROR):
    if err_type == NORMAL_ERROR:
        error_body = {
            'faultstring': faultstring,
            'debuginfo': debuginfo
        }
        raw_error_body = json.dumps(error_body)
        body = {'error_message': raw_error_body}
    elif err_type == ERROR_DICT:
        body = {'error': {'title': faultstring, 'message': debuginfo}}
    elif err_type == ERROR_LIST_WITH_DETAIL:
        main_body = {'title': faultstring, 'detail': debuginfo}
        body = {'errors': [main_body]}
    elif err_type == ERROR_LIST_WITH_DESC:
        main_body = {'title': faultstring, 'description': debuginfo}
        body = {'errors': [main_body]}
    raw_body = json.dumps(body)
    return raw_body


HTTP_CLASS = six.moves.http_client.HTTPConnection
HTTPS_CLASS = http.VerifiedHTTPSConnection
DEFAULT_TIMEOUT = 600


class HttpClientTest(utils.BaseTestCase):

    def test_url_generation_trailing_slash_in_base(self):
        client = http.HTTPClient('http://localhost/')
        url = client._make_connection_url('/v1/resources')
        self.assertEqual('/v1/resources', url)

    def test_url_generation_without_trailing_slash_in_base(self):
        client = http.HTTPClient('http://localhost')
        url = client._make_connection_url('/v1/resources')
        self.assertEqual('/v1/resources', url)

    def test_url_generation_prefix_slash_in_path(self):
        client = http.HTTPClient('http://localhost/')
        url = client._make_connection_url('/v1/resources')
        self.assertEqual('/v1/resources', url)

    def test_url_generation_without_prefix_slash_in_path(self):
        client = http.HTTPClient('http://localhost')
        url = client._make_connection_url('v1/resources')
        self.assertEqual('/v1/resources', url)

    def test_server_exception_empty_body(self):
        error_body = _get_error_body()
        fake_resp = utils.FakeResponse({'content-type': 'application/json'},
                                       six.StringIO(error_body),
                                       version=1,
                                       status=500)
        client = http.HTTPClient('http://localhost/')
        client.get_connection = (
            lambda *a, **kw: utils.FakeConnection(fake_resp))

        error = self.assertRaises(exc.InternalServerError,
                                  client.json_request,
                                  'GET', '/v1/resources')
        self.assertEqual('Internal Server Error (HTTP 500)', str(error))

    def test_server_exception_msg_only(self):
        error_msg = 'test error msg'
        error_body = _get_error_body(error_msg, err_type=ERROR_DICT)
        fake_resp = utils.FakeResponse({'content-type': 'application/json'},
                                       six.StringIO(error_body),
                                       version=1,
                                       status=500)
        client = http.HTTPClient('http://localhost/')
        client.get_connection = (
            lambda *a, **kw: utils.FakeConnection(fake_resp))

        error = self.assertRaises(exc.InternalServerError,
                                  client.json_request,
                                  'GET', '/v1/resources')
        self.assertEqual(error_msg + ' (HTTP 500)', str(error))

    def test_server_exception_msg_and_traceback(self):
        error_msg = 'another test error'
        error_trace = ("\"Traceback (most recent call last):\\n\\n  "
                       "File \\\"/usr/local/lib/python2.7/...")
        error_body = _get_error_body(error_msg, error_trace,
                                     ERROR_LIST_WITH_DESC)
        fake_resp = utils.FakeResponse({'content-type': 'application/json'},
                                       six.StringIO(error_body),
                                       version=1,
                                       status=500)
        client = http.HTTPClient('http://localhost/')
        client.get_connection = (
            lambda *a, **kw: utils.FakeConnection(fake_resp))

        error = self.assertRaises(exc.InternalServerError,
                                  client.json_request,
                                  'GET', '/v1/resources')

        self.assertEqual(
            '%(error)s (HTTP 500)\n%(trace)s' % {'error': error_msg,
                                                 'trace': error_trace},
            "%(error)s\n%(details)s" % {'error': str(error),
                                        'details': str(error.details)})

    def test_server_exception_address(self):
        endpoint = 'https://magnum-host:6385'
        client = http.HTTPClient(endpoint, token='foobar', insecure=True,
                                 ca_file='/path/to/ca_file')
        client.get_connection = (
            lambda *a, **kw: utils.FakeConnection(exc=socket.gaierror))

        self.assertRaises(exc.EndpointNotFound, client.json_request,
                          'GET', '/v1/resources', body='farboo')

    def test_server_exception_socket(self):
        client = http.HTTPClient('http://localhost/', token='foobar')
        client.get_connection = (
            lambda *a, **kw: utils.FakeConnection(exc=socket.error))

        self.assertRaises(exc.ConnectionRefused, client.json_request,
                          'GET', '/v1/resources')

    def test_server_exception_endpoint(self):
        endpoint = 'https://magnum-host:6385'
        client = http.HTTPClient(endpoint, token='foobar', insecure=True,
                                 ca_file='/path/to/ca_file')
        client.get_connection = (
            lambda *a, **kw: utils.FakeConnection(exc=socket.gaierror))

        self.assertRaises(exc.EndpointNotFound, client.json_request,
                          'GET', '/v1/resources', body='farboo')

    def test_get_connection(self):
        endpoint = 'https://magnum-host:6385'
        client = http.HTTPClient(endpoint)
        conn = client.get_connection()
        self.assertTrue(conn, http.VerifiedHTTPSConnection)

    def test_get_connection_exception(self):
        endpoint = 'http://magnum-host:6385/'
        expected = (HTTP_CLASS,
                    ('magnum-host', 6385, ''),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_ssl(self):
        endpoint = 'https://magnum-host:6385'
        expected = (HTTPS_CLASS,
                    ('magnum-host', 6385, ''),
                    {
                        'timeout': DEFAULT_TIMEOUT,
                        'ca_file': None,
                        'cert_file': None,
                        'key_file': None,
                        'insecure': False,
                    })
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_ssl_params(self):
        endpoint = 'https://magnum-host:6385'
        ssl_args = {
            'ca_file': '/path/to/ca_file',
            'cert_file': '/path/to/cert_file',
            'key_file': '/path/to/key_file',
            'insecure': True,
        }

        expected_kwargs = {'timeout': DEFAULT_TIMEOUT}
        expected_kwargs.update(ssl_args)
        expected = (HTTPS_CLASS,
                    ('magnum-host', 6385, ''),
                    expected_kwargs)
        params = http.HTTPClient.get_connection_params(endpoint, **ssl_args)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_timeout(self):
        endpoint = 'http://magnum-host:6385'
        expected = (HTTP_CLASS,
                    ('magnum-host', 6385, ''),
                    {'timeout': 300.0})
        params = http.HTTPClient.get_connection_params(endpoint, timeout=300)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_version(self):
        endpoint = 'http://magnum-host:6385/v1'
        expected = (HTTP_CLASS,
                    ('magnum-host', 6385, ''),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_version_trailing_slash(self):
        endpoint = 'http://magnum-host:6385/v1/'
        expected = (HTTP_CLASS,
                    ('magnum-host', 6385, ''),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_subpath(self):
        endpoint = 'http://magnum-host:6385/magnum'
        expected = (HTTP_CLASS,
                    ('magnum-host', 6385, '/magnum'),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_subpath_trailing_slash(self):
        endpoint = 'http://magnum-host:6385/magnum/'
        expected = (HTTP_CLASS,
                    ('magnum-host', 6385, '/magnum'),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_subpath_version(self):
        endpoint = 'http://magnum-host:6385/magnum/v1'
        expected = (HTTP_CLASS,
                    ('magnum-host', 6385, '/magnum'),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_subpath_version_trailing_slash(self):
        endpoint = 'http://magnum-host:6385/magnum/v1/'
        expected = (HTTP_CLASS,
                    ('magnum-host', 6385, '/magnum'),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_unsupported_scheme(self):
        endpoint = 'foo://magnum-host:6385/magnum/v1/'
        self.assertRaises(exc.EndpointException,
                          http.HTTPClient.get_connection_params, endpoint)

    def test_401_unauthorized_exception(self):
        error_body = _get_error_body(err_type=ERROR_LIST_WITH_DETAIL)
        fake_resp = utils.FakeResponse({'content-type': 'text/plain'},
                                       six.StringIO(error_body),
                                       version=1,
                                       status=401)
        client = http.HTTPClient('http://localhost/')
        client.get_connection = (lambda *a,
                                 **kw: utils.FakeConnection(fake_resp))

        self.assertRaises(exc.Unauthorized, client.json_request,
                          'GET', '/v1/resources')

    def test_server_redirect_exception(self):
        fake_redirect_resp = utils.FakeResponse(
            {'content-type': 'application/octet-stream'},
            'foo', version=1, status=301)
        fake_resp = utils.FakeResponse(
            {'content-type': 'application/octet-stream'},
            'bar', version=1, status=300)
        client = http.HTTPClient('http://localhost/')
        conn = utils.FakeConnection(fake_redirect_resp,
                                    redirect_resp=fake_resp)
        client.get_connection = (lambda *a, **kw: conn)

        self.assertRaises(MultipleChoices, client.json_request,
                          'GET', '/v1/resources')

    def test_server_body_undecode_json(self):
        err = "foo"
        fake_resp = utils.FakeResponse(
            {'content-type': 'application/json'},
            six.StringIO(err), version=1, status=200)
        client = http.HTTPClient('http://localhost/')
        conn = utils.FakeConnection(fake_resp)
        client.get_connection = (lambda *a, **kw: conn)

        resp, body = client.json_request('GET', '/v1/resources')

        self.assertEqual(resp, fake_resp)
        self.assertEqual(err, body)

    def test_server_success_body_app(self):
        fake_resp = utils.FakeResponse(
            {'content-type': 'application/octet-stream'},
            'bar', version=1, status=200)
        client = http.HTTPClient('http://localhost/')
        conn = utils.FakeConnection(fake_resp)
        client.get_connection = (lambda *a, **kw: conn)

        resp, body = client.json_request('GET', '/v1/resources')

        self.assertEqual(resp, fake_resp)
        self.assertIsNone(body)

    def test_server_success_body_none(self):
        fake_resp = utils.FakeResponse(
            {'content-type': None},
            six.StringIO('bar'), version=1, status=200)
        client = http.HTTPClient('http://localhost/')
        conn = utils.FakeConnection(fake_resp)
        client.get_connection = (lambda *a, **kw: conn)

        resp, body = client.json_request('GET', '/v1/resources')

        self.assertEqual(resp, fake_resp)
        self.assertTrue(isinstance(body, list))

    def test_server_success_body_json(self):
        err = _get_error_body()
        fake_resp = utils.FakeResponse(
            {'content-type': 'application/json'},
            six.StringIO(err), version=1, status=200)
        client = http.HTTPClient('http://localhost/')
        conn = utils.FakeConnection(fake_resp)
        client.get_connection = (lambda *a, **kw: conn)

        resp, body = client.json_request('GET', '/v1/resources')

        self.assertEqual(resp, fake_resp)
        self.assertEqual(json.dumps(body), err)

    def test_raw_request(self):
        fake_resp = utils.FakeResponse(
            {'content-type': 'application/octet-stream'},
            'bar', version=1, status=200)
        client = http.HTTPClient('http://localhost/')
        conn = utils.FakeConnection(fake_resp)
        client.get_connection = (lambda *a, **kw: conn)

        resp, body = client.raw_request('GET', '/v1/resources')

        self.assertEqual(resp, fake_resp)
        self.assertIsInstance(body, http.ResponseBodyIterator)


class SessionClientTest(utils.BaseTestCase):

    def test_server_exception_msg_and_traceback(self):
        error_msg = 'another test error'
        error_trace = ("\"Traceback (most recent call last):\\n\\n  "
                       "File \\\"/usr/local/lib/python2.7/...")
        error_body = _get_error_body(error_msg, error_trace)

        fake_session = utils.FakeSession({'Content-Type': 'application/json'},
                                         error_body,
                                         500)

        client = http.SessionClient(session=fake_session)

        error = self.assertRaises(exc.InternalServerError,
                                  client.json_request,
                                  'GET', '/v1/resources')

        self.assertEqual(
            '%(error)s (HTTP 500)\n%(trace)s' % {'error': error_msg,
                                                 'trace': error_trace},
            "%(error)s\n%(details)s" % {'error': str(error),
                                        'details': str(error.details)})

    def test_server_exception_empty_body(self):
        error_body = _get_error_body()

        fake_session = utils.FakeSession({'Content-Type': 'application/json'},
                                         error_body,
                                         500)

        client = http.SessionClient(session=fake_session)

        error = self.assertRaises(exc.InternalServerError,
                                  client.json_request,
                                  'GET', '/v1/resources')

        self.assertEqual('Internal Server Error (HTTP 500)', str(error))

    def test_bypass_url(self):
        fake_response = utils.FakeSessionResponse(
            {}, content="", status_code=201)
        fake_session = mock.MagicMock()
        fake_session.request.side_effect = [fake_response]

        client = http.SessionClient(
            session=fake_session, endpoint_override='http://magnum')

        client.json_request('GET', '/v1/bays')
        self.assertEqual(
            fake_session.request.call_args[1]['endpoint_override'],
            'http://magnum'
        )

    def test_exception(self):
        fake_response = utils.FakeSessionResponse(
            {}, content="", status_code=504)
        fake_session = mock.MagicMock()
        fake_session.request.side_effect = [fake_response]
        client = http.SessionClient(
            session=fake_session, endpoint_override='http://magnum')
        self.assertRaises(GatewayTimeout,
                          client.json_request,
                          'GET', '/v1/resources')

    def test_construct_http_client_return_httpclient(self):
        client = http._construct_http_client('http://localhost/')

        self.assertIsInstance(client, http.HTTPClient)

    def test_construct_http_client_return_sessionclient(self):
        fake_session = mock.MagicMock()
        client = http._construct_http_client(session=fake_session)

        self.assertIsInstance(client, http.SessionClient)

    def test_raw_request(self):
        fake_response = utils.FakeSessionResponse(
            {'content-type': 'application/octet-stream'},
            content="", status_code=200)
        fake_session = mock.MagicMock()
        fake_session.request.side_effect = [fake_response]

        client = http.SessionClient(
            session=fake_session, endpoint_override='http://magnum')

        resp = client.raw_request('GET', '/v1/bays')

        self.assertEqual(
            fake_session.request.call_args[1]['headers']['Content-Type'],
            'application/octet-stream'
        )
        self.assertEqual(fake_response, resp)
