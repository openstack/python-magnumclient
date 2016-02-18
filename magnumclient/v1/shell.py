# Copyright 2014
# The Cloudscaling Group, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from magnumclient.v1 import baymodels_shell
from magnumclient.v1 import bays_shell
from magnumclient.v1 import certificates_shell
from magnumclient.v1 import containers_shell
from magnumclient.v1 import mservices_shell
from magnumclient.v1 import pods_shell
from magnumclient.v1 import replicationcontrollers_shell
from magnumclient.v1 import services_shell

COMMAND_MODULES = [
    baymodels_shell,
    bays_shell,
    certificates_shell,
    containers_shell,
    mservices_shell,
    pods_shell,
    replicationcontrollers_shell,
    services_shell,
]
