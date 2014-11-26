# Copyright 2014
# The Cloudscaling Group, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from keystoneclient.v2_0 import client as keystone_client_v2
from keystoneclient.v3 import client as keystone_client_v3

from magnumclient.api import bays
from magnumclient.api import containers
from magnumclient.api import pods
from magnumclient.api import services
from magnumclient.common import httpclient


class Client(object):
    def __init__(self, username=None, api_key=None, project_id=None,
                 project_name=None, auth_url=None, magnum_url=None,
                 endpoint_type='publicURL', service_type='container',
                 input_auth_token=None):

        if not input_auth_token:
            keystone = self.get_keystone_client(username=username,
                                                api_key=api_key,
                                                auth_url=auth_url,
                                                project_id=project_id,
                                                project_name=project_name)
            input_auth_token = keystone.auth_token
        if not input_auth_token:
            raise RuntimeError("Not Authorized")

        magnum_catalog_url = magnum_url
        if not magnum_url:
            keystone = self.get_keystone_client(username=username,
                                                api_key=api_key,
                                                auth_url=auth_url,
                                                token=input_auth_token,
                                                project_id=project_id,
                                                project_name=project_name)
            catalog = keystone.service_catalog.get_endpoints(service_type)
            if service_type in catalog:
                for e_type, endpoint in catalog.get(service_type)[0].items():
                    if str(e_type).lower() == str(endpoint_type).lower():
                        magnum_catalog_url = endpoint
                        break
        if not magnum_catalog_url:
            raise RuntimeError("Could not find Magnum endpoint in catalog")

        http_cli_kwargs = {
            'token': input_auth_token,
            # TODO(yuanying): - use insecure
            # 'insecure': kwargs.get('insecure'),
            # TODO(yuanying): - use timeout
            # 'timeout': kwargs.get('timeout'),
            # TODO(yuanying): - use ca_file
            # 'ca_file': kwargs.get('ca_file'),
            # TODO(yuanying): - use cert_file
            # 'cert_file': kwargs.get('cert_file'),
            # TODO(yuanying): - use key_file
            # 'key_file': kwargs.get('key_file'),
            'auth_ref': None,
        }
        self.http_client = httpclient.HTTPClient(magnum_catalog_url,
                                                 **http_cli_kwargs)
        self.bays = bays.BayManager(self.http_client)
        self.pods = pods.PodManager(self.http_client)
        self.services = services.ServiceManager(self.http_client)
        self.containers = containers.ContainerManager(self.http_client)

    def get_keystone_client(self, username=None, api_key=None, auth_url=None,
                            token=None, project_id=None, project_name=None):
        if not auth_url:
                raise RuntimeError("No auth url specified")
        imported_client = (keystone_client_v2 if "v2.0" in auth_url
                           else keystone_client_v3)
        if not getattr(self, "keystone_client", None):
            self.keystone_client = imported_client.Client(
                username=username,
                password=api_key,
                token=token,
                tenant_id=project_id,
                tenant_name=project_name,
                auth_url=auth_url,
                endpoint=auth_url)

        self.keystone_client.authenticate()

        return self.keystone_client

    @staticmethod
    def get_projects_list(keystone_client):
        if isinstance(keystone_client, keystone_client_v2.Client):
            return keystone_client.tenants

        return keystone_client.projects
