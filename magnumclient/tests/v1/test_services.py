# Copyright 2015 IBM Corp.
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

import testtools
from testtools import matchers

from magnumclient import exceptions
from magnumclient.tests import utils
from magnumclient.v1 import services


SERVICE1 = {'id': 123,
            'uuid': '66666666-7777-8888-9999-000000000001',
            'name': 'service1',
            'bay_uuid': '5d12f6fd-a196-4bf0-ae4c-1f639a523a51',
            'selector': {'name': 'bar1'},
            'labels': {'name': 'foo1'},
            'ip': '10.0.0.3',
            'port': 8080
            }
SERVICE2 = {'id': 124,
            'uuid': '66666666-7777-8888-9999-000000000002',
            'name': 'service2',
            'bay_uuid': '5d12f6fd-a196-4bf0-ae4c-1f639a523a52',
            'selector': {'name': 'bar2'},
            'labels': {'name': 'foo2'},
            'ip': '10.0.0.4',
            'port': 8081
            }
CREATE_SVC = {'manifest_url': 'file:///a/b.json'}
UPDATED_SVC = copy.deepcopy(SERVICE1)
NEW_SELECTOR = {'name': 'bar3'}
UPDATED_SVC['selector'] = NEW_SELECTOR

fake_responses = {
    '/v1/services':
    {
        'GET': (
            {},
            {'services': [SERVICE1, SERVICE2]},
        ),
        'POST': (
            {},
            CREATE_SVC,
        ),
    },
    '/v1/services/?bay_ident=%s' % (SERVICE1['bay_uuid']):
    {
        'GET': (
            {},
            {'services': [SERVICE1, SERVICE2]},
        ),
        'POST': (
            {},
            CREATE_SVC,
        ),
    },
    '/v1/services/%s/?bay_ident=%s' % (SERVICE1['id'],
                                       SERVICE1['bay_uuid']):
    {
        'GET': (
            {},
            SERVICE1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_SVC,
        ),
    },
    '/v1/services/%s/?bay_ident=%s' % (SERVICE1['name'],
                                       SERVICE1['bay_uuid']):
    {
        'GET': (
            {},
            SERVICE1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_SVC,
        ),
    },
}


class ServiceManagerTest(testtools.TestCase):

    def setUp(self):
        super(ServiceManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = services.ServiceManager(self.api)

    def test_coe_service_list(self):
        services = self.mgr.list(SERVICE1['bay_uuid'])
        expect = [
            ('GET', '/v1/services/?bay_ident=%s' % (SERVICE1['bay_uuid']),
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(services, matchers.HasLength(2))

    def test_coe_service_show_by_id(self):
        service = self.mgr.get(SERVICE1['id'], SERVICE1['bay_uuid'])
        expect = [
            ('GET', '/v1/services/%s/?bay_ident=%s' % (SERVICE1['id'],
                                                       SERVICE1['bay_uuid']),
             {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(SERVICE1['name'], service.name)
        self.assertEqual(SERVICE1['bay_uuid'], service.bay_uuid)
        self.assertEqual(SERVICE1['ip'], service.ip)

    def test_coe_service_show_by_name(self):
        service = self.mgr.get(SERVICE1['name'], SERVICE1['bay_uuid'])
        expect = [
            ('GET', '/v1/services/%s/?bay_ident=%s' % (SERVICE1['name'],
                                                       SERVICE1['bay_uuid']),
             {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(SERVICE1['name'], service.name)
        self.assertEqual(SERVICE1['bay_uuid'], service.bay_uuid)
        self.assertEqual(SERVICE1['ip'], service.ip)

    def test_coe_service_create(self):
        service = self.mgr.create(**CREATE_SVC)
        expect = [
            ('POST', '/v1/services', {}, CREATE_SVC),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(service)

    def test_coe_service_create_fail(self):
        CREATE_SVC_FAIL = copy.deepcopy(CREATE_SVC)
        CREATE_SVC_FAIL["wrong_key"] = "wrong"
        self.assertRaisesRegexp(exceptions.InvalidAttribute,
                                ("Key must be in %s" %
                                 ','.join(services.CREATION_ATTRIBUTES)),
                                self.mgr.create, **CREATE_SVC_FAIL)
        self.assertEqual([], self.api.calls)

    def test_coe_service_delete_by_id(self):
        service = self.mgr.delete(SERVICE1['id'], SERVICE1['bay_uuid'])
        expect = [
            ('DELETE', '/v1/services/%s/?bay_ident=%s' % (
                SERVICE1['id'], SERVICE1['bay_uuid']), {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(service)

    def test_coe_service_delete_by_name(self):
        service = self.mgr.delete(SERVICE1['name'], SERVICE1['bay_uuid'])
        expect = [
            ('DELETE', '/v1/services/%s/?bay_ident=%s' % (
                SERVICE1['name'], SERVICE1['bay_uuid']), {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(service)

    def test_coe_service_update(self):
        patch = {'op': 'replace',
                 'value': NEW_SELECTOR,
                 'path': '/selector'}
        service = self.mgr.update(service_id=SERVICE1['id'],
                                  bay_ident=SERVICE1['bay_uuid'],
                                  patch=patch)
        expect = [
            ('PATCH', '/v1/services/%s/?bay_ident=%s' % (
                SERVICE1['id'], SERVICE1['bay_uuid']), {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_SELECTOR, service.selector)
