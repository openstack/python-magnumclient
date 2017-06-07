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
from magnumclient.common import utils
from magnumclient import exceptions


CREATION_ATTRIBUTES = ['name', 'image_id', 'flavor_id', 'master_flavor_id',
                       'keypair_id', 'external_network_id', 'fixed_network',
                       'fixed_subnet', 'dns_nameserver', 'docker_volume_size',
                       'labels', 'coe', 'http_proxy', 'https_proxy',
                       'no_proxy', 'network_driver', 'tls_disabled', 'public',
                       'registry_enabled', 'volume_driver', 'server_type',
                       'docker_storage_driver', 'master_lb_enabled',
                       'floating_ip_enabled']

OUTPUT_ATTRIBUTES = CREATION_ATTRIBUTES + ['apiserver_port', 'created_at',
                                           'insecure_registry', 'links',
                                           'updated_at', 'cluster_distro',
                                           'uuid']


class BaseModel(base.Resource):
    # model_name needs to be overridden by any derived class.
    # model_name should be capitalized and singular, e.g. "Cluster"
    model_name = ''

    def __repr__(self):
        return "<" + self.__class__.model_name + "%s>" % self._info


class BaseModelManager(base.Manager):
    # api_name needs to be overridden by any derived class.
    # api_name should be pluralized and lowercase, e.g. "clustertemplates", as
    # it shows up in the URL path: "/v1/{api_name}"
    api_name = ''

    @classmethod
    def _path(cls, id=None):
        return '/v1/' + cls.api_name + \
               '/%s' % id if id else '/v1/' + cls.api_name

    def list(self, limit=None, marker=None, sort_key=None,
             sort_dir=None, detail=False):
        """Retrieve a list of baymodels.

        :param marker: Optional, the UUID of a baymodel, eg the last
                       baymodel from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of baymodels to return.
            2) limit == 0, return the entire list of baymodels.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Magnum API
               (see Magnum's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about baymodels.

        :returns: A list of baymodels.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(marker, limit, sort_key, sort_dir)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), self.__class__.api_name)
        else:
            return self._list_pagination(self._path(path),
                                         self.__class__.api_name,
                                         limit=limit)

    def get(self, id):
        try:
            return self._list(self._path(id))[0]
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

    def delete(self, id):
        return self._delete(self._path(id))

    def update(self, id, patch):
        return self._update(self._path(id), patch)
