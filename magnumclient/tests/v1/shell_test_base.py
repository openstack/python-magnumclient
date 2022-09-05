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

import re
from unittest import mock

from testtools import matchers

from magnumclient.tests import utils

FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_PROJECT_NAME': 'project_name',
            'OS_AUTH_URL': 'http://no.where/v2.0',
            'BYPASS_URL': 'http://magnum'}


class TestCommandLineArgument(utils.TestCase):
    _unrecognized_arg_error = [
        r'.*?^usage: ',
        r'.*?^error: unrecognized arguments:',
        r".*?^Try 'magnum help ' for more information.",
        ]

    _mandatory_group_arg_error = [
        r'.*?^usage: ',
        r'.*?^error: one of the arguments',
        r".*?^Try 'magnum help ",
    ]

    _too_many_group_arg_error = [
        r'.*?^usage: ',
        r'.*?^error: (argument \-\-[a-z\-]*: not allowed with argument )',
        r".*?^Try 'magnum help ",
    ]

    _mandatory_arg_error = [
        r'.*?^usage: ',
        r'.*?^error: (the following arguments|argument)',
        r".*?^Try 'magnum help ",
    ]

    _duplicate_arg_error = [
        r'.*?^usage: ',
        r'.*?^error: (Duplicate "<.*>" arguments:)',
        r".*?^Try 'magnum help ",
    ]

    _deprecated_warning = [
        r'.*(WARNING: The \-\-[a-z\-]* parameter is deprecated)+',
        (r'.*(Use the [\<\-a-z\-\>]* (positional )*parameter to avoid seeing '
         'this message)+')
    ]

    _few_argument_error = [
        r'.*?^usage: magnum ',
        r'.*?^error: (the following arguments|too few arguments)',
        r".*?^Try 'magnum help ",
    ]

    _invalid_value_error = [
        r'.*?^usage: ',
        r'.*?^error: argument .*: invalid .* value:',
        r".*?^Try 'magnum help ",
    ]

    def setUp(self):
        super(TestCommandLineArgument, self).setUp()
        self.make_env(fake_env=FAKE_ENV)
        session_client = mock.patch(
            'magnumclient.common.httpclient.SessionClient')
        session_client.start()
        loader = mock.patch('keystoneauth1.loading.get_plugin_loader')
        loader.start()
        session = mock.patch('keystoneauth1.session.Session')
        session.start()

        self.addCleanup(session_client.stop)
        self.addCleanup(loader.stop)
        self.addCleanup(session.stop)

    def _test_arg_success(self, command, keyword=None):
        stdout, stderr = self.shell(command)
        if keyword:
            self.assertIn(keyword, (stdout + stderr))

    def _test_arg_failure(self, command, error_msg):
        stdout, stderr = self.shell(command, (2,))
        for line in error_msg:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(line,
                            re.DOTALL | re.MULTILINE))
