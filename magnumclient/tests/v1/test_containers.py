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
from magnumclient.v1 import containers


CONTAINER1 = {'id': 123,
              'uuid': '66666666-7777-8888-9999-000000000001',
              'bay_uuid': '25d5d872-1f4e-4134-ae15-c5fa38cb09a3',
              'name': 'container1',
              'image': 'c-image1',
              'command': 'c-command1',
              'memory': '512m',
              }
CONTAINER2 = {'id': 124,
              'uuid': '66666666-7777-8888-9999-000000000002',
              'bay_uuid': '25d5d872-1f4e-4134-ae15-c5fa38cb09a3',
              'name': 'container1',
              'image': 'c-image2',
              'command': 'c-command2',
              'memory': '2g',
              }

CREATE_CONTAINER = copy.deepcopy(CONTAINER1)
del CREATE_CONTAINER['id']
del CREATE_CONTAINER['uuid']

UPDATED_CONTAINER = copy.deepcopy(CONTAINER1)
NEW_NAME = 'newcontainer'
UPDATED_CONTAINER['name'] = NEW_NAME

fake_responses = {
    '/v1/containers':
    {
        'GET': (
            {},
            {'containers': [CONTAINER1, CONTAINER2]},
        ),
        'POST': (
            {},
            CREATE_CONTAINER,
        ),
    },
    '/v1/containers/?bay_ident=25d5d872-1f4e-4134-ae15-c5fa38cb09a3':
    {
        'GET': (
            {},
            {'containers': [CONTAINER1, CONTAINER2]},
        ),
        'POST': (
            {},
            CREATE_CONTAINER,
        ),
    },
    '/v1/containers/%s' % CONTAINER1['id']:
    {
        'GET': (
            {},
            CONTAINER1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_CONTAINER,
        ),
    },
    '/v1/containers/%s' % CONTAINER1['name']:
    {
        'GET': (
            {},
            CONTAINER1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_CONTAINER,
        ),
    },
    '/v1/containers/%s/start' % CONTAINER1['id']:
    {
        'PUT': (
            {},
            CONTAINER1,
        ),
    },
    '/v1/containers/%s/start' % CONTAINER1['name']:
    {
        'PUT': (
            {},
            CONTAINER1,
        ),
    },
    '/v1/containers/%s/stop' % CONTAINER1['id']:
    {
        'PUT': (
            {},
            CONTAINER1,
        ),
    },
    '/v1/containers/%s/stop' % CONTAINER1['name']:
    {
        'PUT': (
            {},
            CONTAINER1,
        ),
    },
    '/v1/containers/%s/pause' % CONTAINER1['id']:
    {
        'PUT': (
            {},
            CONTAINER1,
        ),
    },
    '/v1/containers/%s/pause' % CONTAINER1['name']:
    {
        'PUT': (
            {},
            CONTAINER1,
        ),
    },
    '/v1/containers/%s/unpause' % CONTAINER1['id']:
    {
        'PUT': (
            {},
            CONTAINER1,
        ),
    },
    '/v1/containers/%s/unpause' % CONTAINER1['name']:
    {
        'PUT': (
            {},
            CONTAINER1,
        ),
    },
    '/v1/containers/%s/reboot' % CONTAINER1['id']:
    {
        'PUT': (
            {},
            CONTAINER1,
        ),
    },
    '/v1/containers/%s/reboot' % CONTAINER1['name']:
    {
        'PUT': (
            {},
            CONTAINER1,
        ),
    },
    '/v1/containers/%s/logs' % CONTAINER1['id']:
    {
        'GET': (
            {},
            {'output': 'login now'},
        ),
    },
    '/v1/containers/%s/logs' % CONTAINER1['name']:
    {
        'GET': (
            {},
            {'output': 'login now'},
        ),
    },
    '/v1/containers/%s/execute?command=ls' % CONTAINER1['id']:
    {
        'PUT': (
            {},
            {'output': '/home'},
        ),
    },
    '/v1/containers/%s/execute?command=ls' % CONTAINER1['name']:
    {
        'PUT': (
            {},
            {'output': '/home'},
        ),
    },
    '/v1/containers/?limit=2':
    {
        'GET': (
            {},
            {'containers': [CONTAINER1, CONTAINER2]},
        ),
    },
    '/v1/containers/?marker=%s' % CONTAINER2['uuid']:
    {
        'GET': (
            {},
            {'containers': [CONTAINER1, CONTAINER2]},
        ),
    },
    '/v1/containers/?limit=2&marker=%s' % CONTAINER2['uuid']:
    {
        'GET': (
            {},
            {'containers': [CONTAINER1, CONTAINER2]},
        ),
    },
    '/v1/containers/?sort_dir=asc':
    {
        'GET': (
            {},
            {'containers': [CONTAINER1, CONTAINER2]},
        ),
    },
    '/v1/containers/?sort_key=uuid':
    {
        'GET': (
            {},
            {'containers': [CONTAINER1, CONTAINER2]},
        ),
    },
    '/v1/containers/?sort_key=uuid&sort_dir=desc':
    {
        'GET': (
            {},
            {'containers': [CONTAINER2, CONTAINER1]},
        ),
    },
}


class ContainerManagerTest(testtools.TestCase):

    def setUp(self):
        super(ContainerManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = containers.ContainerManager(self.api)

    def test_container_list(self):
        containers = self.mgr.list()
        expect = [
            ('GET', '/v1/containers', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(containers, matchers.HasLength(2))

    def test_container_list_with_bay(self):
        containers = self.mgr.list(
            bay_ident='25d5d872-1f4e-4134-ae15-c5fa38cb09a3')
        expect = [
            ('GET', '/v1/containers/?bay_ident=25d5d872-1f4e-4134'
                    '-ae15-c5fa38cb09a3', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(containers, matchers.HasLength(2))

    def _test_container_list_with_filters(
            self, limit=None, marker=None,
            sort_key=None, sort_dir=None,
            detail=False, expect=[]):
        containers_filter = self.mgr.list(limit=limit, marker=marker,
                                          sort_key=sort_key,
                                          sort_dir=sort_dir,
                                          detail=detail)
        self.assertEqual(expect, self.api.calls)
        self.assertThat(containers_filter, matchers.HasLength(2))

    def test_container_list_with_limit(self):
        expect = [
            ('GET', '/v1/containers/?limit=2', {}, None),
        ]
        self._test_container_list_with_filters(
            limit=2,
            expect=expect)

    def test_container_list_with_marker(self):
        expect = [
            ('GET', '/v1/containers/?marker=%s' % CONTAINER2['uuid'],
             {}, None),
        ]
        self._test_container_list_with_filters(
            marker=CONTAINER2['uuid'],
            expect=expect)

    def test_container_list_with_marker_limit(self):
        expect = [
            ('GET', '/v1/containers/?limit=2&marker=%s' % CONTAINER2['uuid'],
             {}, None),
        ]
        self._test_container_list_with_filters(
            limit=2, marker=CONTAINER2['uuid'],
            expect=expect)

    def test_container_list_with_sort_dir(self):
        expect = [
            ('GET', '/v1/containers/?sort_dir=asc',
             {}, None),
        ]
        self._test_container_list_with_filters(
            sort_dir='asc',
            expect=expect)

    def test_container_list_with_sort_key(self):
        expect = [
            ('GET', '/v1/containers/?sort_key=uuid',
             {}, None),
        ]
        self._test_container_list_with_filters(
            sort_key='uuid',
            expect=expect)

    def test_container_list_with_sort_key_dir(self):
        expect = [
            ('GET', '/v1/containers/?sort_key=uuid&sort_dir=desc',
             {}, None),
        ]
        self._test_container_list_with_filters(
            sort_key='uuid', sort_dir='desc',
            expect=expect)

    def test_container_show(self):
        container = self.mgr.get(CONTAINER1['id'])
        expect = [
            ('GET', '/v1/containers/%s' % CONTAINER1['id'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CONTAINER1['name'], container.name)
        self.assertEqual(CONTAINER1['image'], container.image)
        self.assertEqual(CONTAINER1['command'], container.command)
        self.assertEqual(CONTAINER1['memory'], container.memory)

    def test_container_create(self):
        container = self.mgr.create(**CREATE_CONTAINER)
        expect = [
            ('POST', '/v1/containers', {}, CREATE_CONTAINER),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(container)

    def test_container_create_fail(self):
        CREATE_CONTAINER_FAIL = copy.deepcopy(CREATE_CONTAINER)
        CREATE_CONTAINER_FAIL["wrong_key"] = "wrong"
        self.assertRaisesRegexp(exceptions.InvalidAttribute,
                                ("Key must be in %s" %
                                 ','.join(containers.CREATION_ATTRIBUTES)),
                                self.mgr.create, **CREATE_CONTAINER_FAIL)
        self.assertEqual([], self.api.calls)

    def test_container_delete(self):
        container = self.mgr.delete(CONTAINER1['id'])
        expect = [
            ('DELETE', '/v1/containers/%s' % CONTAINER1['id'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(container)

    def test_container_start(self):
        container = self.mgr.start(CONTAINER1['id'])
        expect = [
            ('PUT', '/v1/containers/%s/start' % CONTAINER1['id'],
                    {'Content-Length': '0'}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(container)

    def test_container_stop(self):
        container = self.mgr.stop(CONTAINER1['id'])
        expect = [
            ('PUT', '/v1/containers/%s/stop' % CONTAINER1['id'],
                    {'Content-Length': '0'}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(container)

    def test_container_reboot(self):
        container = self.mgr.reboot(CONTAINER1['id'])
        expect = [
            ('PUT', '/v1/containers/%s/reboot' % CONTAINER1['id'],
                    {'Content-Length': '0'}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(container)

    def test_container_pause(self):
        container = self.mgr.pause(CONTAINER1['id'])
        expect = [
            ('PUT', '/v1/containers/%s/pause' % CONTAINER1['id'],
                    {'Content-Length': '0'}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(container)

    def test_container_unpause(self):
        container = self.mgr.unpause(CONTAINER1['id'])
        expect = [
            ('PUT', '/v1/containers/%s/unpause' % CONTAINER1['id'],
                    {'Content-Length': '0'}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(container)

    def test_container_logs(self):
        logs = self.mgr.logs(CONTAINER1['id'])
        expect = [
            ('GET', '/v1/containers/%s/logs' % CONTAINER1['id'],
                    {'Content-Length': '0'}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual('login now', logs)

    def test_container_execute(self):
        output = self.mgr.execute(CONTAINER1['id'], 'ls')
        expect = [
            ('PUT', '/v1/containers/%s/execute?command=ls' % CONTAINER1['id'],
                    {'Content-Length': '0'}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual('/home', output)
