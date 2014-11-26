# Copyright 2014 NEC Corporation.  All rights reserved.
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

from magnumclient.api import shell
from magnumclient.tests import base


container_fixture = {
    "name": "container",
    "desc": "container description."
}


class ShellTest(base.TestCase):

    def setUp(self):
        super(ShellTest, self).setUp()

    def test_do_container_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.json.read.return_value = json.dumps(container_fixture)

        shell.do_container_create(client_mock, args)
        client_mock.containers.create.assert_called_once_with(
            **container_fixture)

    def test_do_container_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        shell.do_container_list(client_mock, args)
        client_mock.containers.list.assert_called_once_with()

    def test_do_container_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = "container_id"
        args.id = container_id

        shell.do_container_delete(client_mock, args)
        client_mock.containers.delete.assert_called_once_with(container_id)

    def test_do_container_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        container_id = "container_id"
        args.id = container_id
        args.json = None

        shell.do_container_show(client_mock, args)
        client_mock.containers.get.assert_called_once_with(container_id)
