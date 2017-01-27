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

from magnumclient.common import utils
from magnumclient import exceptions
from magnumclient.v1 import basemodels


CREATION_ATTRIBUTES = ['project_id', 'resource', 'hard_limit']


class Quotas(basemodels.BaseModel):
    model_name = "Quotas"


class QuotasManager(basemodels.BaseModelManager):
    api_name = "quotas"
    resource_class = Quotas

    @staticmethod
    def _path(id=None, resource=None):
        if not id:
            return '/v1/quotas'

        return '/v1/quotas/%(id)s/%(res)s' % {'id': id, 'res': resource}

    def list(self, limit=None, marker=None, sort_key=None,
             sort_dir=None, all_tenants=False):

        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(marker, limit, sort_key, sort_dir)

        if all_tenants:
            filters.append('all_tenants=True')

        path = self._path()
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(path, self.api_name)
        else:
            return self._list_pagination(path, self.api_name,
                                         limit=limit)

    def get(self, id, resource):
        try:
            return self._list(self._path(id, resource))[0]
        except IndexError:
            return None

    def create(self, **kwargs):
        new = {}
        for (key, value) in kwargs.items():
            if key in CREATION_ATTRIBUTES:
                new[key] = value
            else:
                raise exceptions.InvalidAttribute(
                    "Key must be in %s" % ",".join(CREATION_ATTRIBUTES))
        return self._create(self._path(), new)

    def delete(self, id, resource):
        return self._delete(self._path(id, resource))

    def update(self, id, resource, patch):
        url = self._path(id, resource)
        return self._update(url, patch)
