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

from magnumclient.v1 import basemodels


CLUSTER_TEMPLATE_ATTRIBUTES = [
    'insecure_registry',
    'labels',
    'updated_at',
    'floating_ip_enabled',
    'fixed_subnet',
    'master_flavor_id',
    'uuid',
    'no_proxy',
    'https_proxy',
    'tls_disabled',
    'keypair_id',
    'public',
    'http_proxy',
    'docker_volume_size',
    'server_type',
    'external_network_id',
    'cluster_distro',
    'image_id',
    'volume_driver',
    'registry_enabled',
    'docker_storage_driver',
    'apiserver_port',
    'name',
    'created_at',
    'network_driver',
    'fixed_network',
    'coe',
    'flavor_id',
    'master_lb_enabled',
    'dns_nameserver',
    'project_id',
    'hidden',
    'tags',
    'driver',
]

CREATION_ATTRIBUTES = basemodels.CREATION_ATTRIBUTES
CREATION_ATTRIBUTES.append('insecure_registry')
CREATION_ATTRIBUTES.append('driver')


class ClusterTemplate(basemodels.BaseModel):
    model_name = "ClusterTemplate"


class ClusterTemplateManager(basemodels.BaseModelManager):
    api_name = "clustertemplates"
    resource_class = ClusterTemplate
