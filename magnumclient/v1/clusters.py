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

from magnumclient.v1 import baseunit


CREATION_ATTRIBUTES = baseunit.CREATION_ATTRIBUTES
CREATION_ATTRIBUTES.append('cluster_template_id')
CREATION_ATTRIBUTES.append('create_timeout')
CREATION_ATTRIBUTES.append('keypair')


class Cluster(baseunit.BaseTemplate):
    template_name = "Clusters"


class ClusterManager(baseunit.BaseTemplateManager):
    resource_class = Cluster
    template_name = 'clusters'
