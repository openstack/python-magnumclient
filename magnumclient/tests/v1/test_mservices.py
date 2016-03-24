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

import testtools
from testtools import matchers

from magnumclient.tests import utils
from magnumclient.v1 import mservices


SERVICE1 = {'id': 123,
            'host': 'fake-host1',
            'binary': 'fake-bin1',
            'state': 'up',
            }
SERVICE2 = {'id': 124,
            'host': 'fake-host2',
            'binary': 'fake-bin2',
            'state': 'down',
            }

fake_responses = {
    '/v1/mservices':
    {
        'GET': (
            {},
            {'mservices': [SERVICE1, SERVICE2]},
        ),
    },
    '/v1/mservices/?limit=2':
    {
        'GET': (
            {},
            {'mservices': [SERVICE1, SERVICE2]},
        ),
    },
    '/v1/mservices/?marker=%s' % SERVICE2['id']:
    {
        'GET': (
            {},
            {'mservices': [SERVICE1, SERVICE2]},
        ),
    },
    '/v1/mservices/?limit=2&marker=%s' % SERVICE2['id']:
    {
        'GET': (
            {},
            {'mservices': [SERVICE2, SERVICE1]},
        ),
    },
    '/v1/mservices/?sort_dir=asc':
    {
        'GET': (
            {},
            {'mservices': [SERVICE1, SERVICE2]},
        ),
    },
    '/v1/mservices/?sort_key=id':
    {
        'GET': (
            {},
            {'mservices': [SERVICE1, SERVICE2]},
        ),
    },
    '/v1/mservices/?sort_key=id&sort_dir=desc':
    {
        'GET': (
            {},
            {'mservices': [SERVICE2, SERVICE1]},
        ),
    },
}


class MServiceManagerTest(testtools.TestCase):

    def setUp(self):
        super(MServiceManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = mservices.MServiceManager(self.api)

    def test_coe_service_list(self):
        mservices = self.mgr.list()
        expect = [
            ('GET', '/v1/mservices', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(mservices, matchers.HasLength(2))

    def _test_coe_service_list_with_filters(
            self, limit=None, marker=None,
            sort_key=None, sort_dir=None,
            detail=False, expect=[]):
        mservices_filter = self.mgr.list(limit=limit, marker=marker,
                                         sort_key=sort_key,
                                         sort_dir=sort_dir,
                                         detail=detail)
        self.assertEqual(expect, self.api.calls)
        self.assertThat(mservices_filter, matchers.HasLength(2))

    def test_coe_service_list_with_limit(self):
        expect = [
            ('GET', '/v1/mservices/?limit=2', {}, None),
        ]
        self._test_coe_service_list_with_filters(
            limit=2,
            expect=expect)

    def test_coe_service_list_with_marker(self):
        expect = [
            ('GET', '/v1/mservices/?marker=%s' % SERVICE2['id'],
             {}, None),
        ]
        self._test_coe_service_list_with_filters(
            marker=SERVICE2['id'],
            expect=expect)

    def test_coe_service_list_with_marker_limit(self):
        expect = [
            ('GET', '/v1/mservices/?limit=2&marker=%s' % SERVICE2['id'],
             {}, None),
        ]
        self._test_coe_service_list_with_filters(
            limit=2, marker=SERVICE2['id'],
            expect=expect)

    def test_coe_service_list_with_sort_dir(self):
        expect = [
            ('GET', '/v1/mservices/?sort_dir=asc',
             {}, None),
        ]
        self._test_coe_service_list_with_filters(
            sort_dir='asc',
            expect=expect)

    def test_coe_service_list_with_sort_key(self):
        expect = [
            ('GET', '/v1/mservices/?sort_key=id',
             {}, None),
        ]
        self._test_coe_service_list_with_filters(
            sort_key='id',
            expect=expect)

    def test_coe_service_list_with_sort_key_dir(self):
        expect = [
            ('GET', '/v1/mservices/?sort_key=id&sort_dir=desc',
             {}, None),
        ]
        self._test_coe_service_list_with_filters(
            sort_key='id', sort_dir='desc',
            expect=expect)
