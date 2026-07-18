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
import datetime
import io
import queue

import fixtures
from oslo_serialization import jsonutils
from oslo_utils import timeutils
import testtools

from magnumclient.common import httpclient as http

FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_PROJECT_NAME': 'project_name',
            'OS_AUTH_URL': 'http://no.where/v2.0'}


class BaseTestCase(testtools.TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.useFixture(fixtures.FakeLogger())


class FakeAPI(object):
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def _request(self, method, url, headers=None, body=None):
        call = (method, url, headers or {}, body)
        self.calls.append(call)
        return self.responses[url][method]

    def raw_request(self, *args, **kwargs):
        response = self._request(*args, **kwargs)
        body_iter = http.ResponseBodyIterator(io.StringIO(response[1]))
        return FakeResponse(response[0]), body_iter

    def json_request(self, *args, **kwargs):
        response = self._request(*args, **kwargs)
        return FakeResponse(response[0]), response[1]


class FakeConnection(object):
    def __init__(self, response=None, **kwargs):
        self._response = queue.Queue()
        self._response.put(response)
        self._last_request = None
        self._exc = kwargs['exc'] if 'exc' in kwargs else None
        if 'redirect_resp' in kwargs:
            self._response.put(kwargs['redirect_resp'])

    def request(self, method, conn_url, **kwargs):
        self._last_request = (method, conn_url, kwargs)
        if self._exc:
            raise self._exc

    def setresponse(self, response):
        self._response = response

    def getresponse(self):
        return self._response.get()


class FakeResponse(object):
    def __init__(self, headers, body=None, version=None, status=None,
                 reason=None):
        """Fake object to help testing.

        :param headers: dict representing HTTP response headers
        :param body: file-like object
        """
        self.headers = headers
        self.body = body
        self.version = version
        self.status = status
        self.reason = reason

    def __getitem__(self, key):
        if key == 'location':
            return 'fake_url'
        else:
            return None

    def getheaders(self):
        return copy.deepcopy(self.headers).items()

    def getheader(self, key, default):
        return self.headers.get(key, default)

    def read(self, amt):
        return self.body.read(amt)


class FakeServiceCatalog(object):
    def url_for(self, endpoint_type, service_type, attr=None,
                filter_value=None):
        if attr == 'region' and filter_value:
            return 'http://regionhost:6385/v1/f14b41234'
        else:
            return 'http://localhost:6385/v1/f14b41234'


class FakeKeystone(object):
    service_catalog = FakeServiceCatalog()
    timestamp = timeutils.utcnow() + datetime.timedelta(days=5)

    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.auth_ref = {
            'token': {'expires': FakeKeystone.timestamp.strftime(
                      '%Y-%m-%dT%H:%M:%S.%f'),
                      'id': 'd1a541311782870742235'}
        }


class FakeSessionResponse(object):

    def __init__(self, headers, content=None, status_code=None):
        self.headers = headers
        self.content = content
        self.status_code = status_code

    def json(self):
        if self.content is not None:
            return jsonutils.loads(self.content)
        else:
            return {}


class FakeSession(object):

    def __init__(self, headers, content=None, status_code=None):
        self.headers = headers
        self.content = content
        self.status_code = status_code

    def request(self, url, method, **kwargs):
        return FakeSessionResponse(self.headers, self.content,
                                   self.status_code)
