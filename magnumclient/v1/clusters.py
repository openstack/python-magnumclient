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
CREATION_ATTRIBUTES.append('docker_volume_size')
CREATION_ATTRIBUTES.append('labels')
CREATION_ATTRIBUTES.append('master_flavor_id')
CREATION_ATTRIBUTES.append('flavor_id')
CREATION_ATTRIBUTES.append('fixed_network')
CREATION_ATTRIBUTES.append('fixed_subnet')
CREATION_ATTRIBUTES.append('floating_ip_enabled')


class Cluster(baseunit.BaseTemplate):
    template_name = "Clusters"


class ClusterManager(baseunit.BaseTemplateManager):
    resource_class = Cluster
    template_name = 'clusters'

    def resize(self, cluster_uuid, node_count,
               nodes_to_remove=[], nodegroup=None):
        url = self._path(cluster_uuid) + "/actions/resize"

        post_body = {"node_count": node_count}
        if nodes_to_remove:
            post_body.update({"nodes_to_remove": nodes_to_remove})
        if nodegroup:
            post_body.update({"nodegroup": nodegroup})

        resp, resp_body = self.api.json_request("POST", url, body=post_body)

        if resp_body:
            return self.resource_class(self, resp_body)

    def upgrade(self, cluster_uuid, cluster_template,
                max_batch_size=1, nodegroup=None):
        url = self._path(cluster_uuid) + "/actions/upgrade"

        post_body = {"cluster_template": cluster_template}
        if max_batch_size:
            post_body.update({"max_batch_size": max_batch_size})
        if nodegroup:
            post_body.update({"nodegroup": nodegroup})

        resp, resp_body = self.api.json_request("POST", url, body=post_body)

        if resp_body:
            return self.resource_class(self, resp_body)
