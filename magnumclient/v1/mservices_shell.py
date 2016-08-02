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


from magnumclient.common import cliutils as utils
from magnumclient.common import utils as magnum_utils


def do_service_list(cs, args):
    """Print a list of magnum services."""
    mservices = cs.mservices.list()
    columns = ('id', 'host', 'binary', 'state', 'disabled',
               'disabled_reason', 'created_at', 'updated_at')

    utils.print_list(mservices, columns,
                     {'versions': magnum_utils.print_list_field('versions')})
