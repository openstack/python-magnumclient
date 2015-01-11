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

from magnumclient.tests import utils
from magnumclient.v1 import pods


POD1 = {'id': 123,
        'uuid': '66666666-7777-8888-9999-000000000000',
        'name': 'pod1',
        'desc': "desc",
        'bay_uuid': '5d12f6fd-a196-4bf0-ae4c-1f639a523a52',
        'images': ['image1', 'image2'],
        'labels': {'foo': 'bar'},
        'status': 'Running'
        }
POD2 = {'id': 124,
        'uuid': '66666666-7777-8888-9999-000000000001',
        'name': 'pod1',
        'desc': "desc",
        'bay_uuid': '5d12f6fd-a196-4bf0-ae4c-1f639a523a53',
        'images': ['image1', 'image2'],
        'labels': {'foo': 'bar'},
        'status': 'Running'
        }
CREATE_POD = {'pod_definition_url': 'file:///a/b.json'}
UPDATED_POD = copy.deepcopy(POD1)
NEW_DESCR = 'new-description'
UPDATED_POD['description'] = NEW_DESCR

fake_responses = {
    '/v1/pods':
    {
        'GET': (
            {},
            {'pods': [POD1, POD2]},
        ),
        'POST': (
            {},
            CREATE_POD,
        ),
    },
    '/v1/pods/%s' % POD1['id']:
    {
        'GET': (
            {},
            POD1
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_POD,
        ),
    },
}


class PodManagerTest(testtools.TestCase):

    def setUp(self):
        super(PodManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = pods.PodManager(self.api)

    def test_pod_list(self):
        pods = self.mgr.list()
        expect = [
            ('GET', '/v1/pods', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(pods, matchers.HasLength(2))

    def test_pod_show(self):
        pod = self.mgr.get(POD1['id'])
        expect = [
            ('GET', '/v1/pods/%s' % POD1['id'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(POD1['name'], pod.name)
        self.assertEqual(POD1['desc'], pod.desc)

    def test_pod_create(self):
        pod = self.mgr.create(**CREATE_POD)
        expect = [
            ('POST', '/v1/pods', {}, CREATE_POD),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(pod)

    def test_pod_delete(self):
        pod = self.mgr.delete(POD1['id'])
        expect = [
            ('DELETE', '/v1/pods/%s' % POD1['id'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(pod)

    def test_pod_update(self):
        patch = {'op': 'replace',
                 'value': NEW_DESCR,
                 'path': '/description'}
        pod = self.mgr.update(id=POD1['id'], patch=patch)
        expect = [
            ('PATCH', '/v1/pods/%s' % POD1['id'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_DESCR, pod.description)
