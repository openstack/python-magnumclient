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

from magnumclient.common import base


class Cluster(base.Resource):
    def __repr__(self):
        return "<Cluster %s>" % self._info


class CredentialManager(base.Manager):
    api_name = "credentials"
    resource_class = Cluster

    @staticmethod
    def _path(id=None):
        return "/v1/credentials/%s" % id

    def update(self, id):
        resp, resp_body = self.api.json_request('PATCH', self._path(id=id))
        return self.resource_class(self, resp_body)
