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

from magnumclient.common import base
from magnumclient.common import utils
from magnumclient import exceptions


# Derived classes may append their own custom attributes to this default list
CREATION_ATTRIBUTES = ['name', 'node_count', 'discovery_url', 'master_count']


class BaseTemplate(base.Resource):
    # template_name must be overridden by any derived class.
    # template_name should be an uppercase plural, e.g. "Clusters"
    template_name = ''

    def __repr__(self):
        return "<" + self.__class__.template_name + " %s>" % self._info


class BaseTemplateManager(base.Manager):
    # template_name must be overridden by any derived class.
    # template_name should be a lowercase plural, e.g. "clusters"
    template_name = ''

    @classmethod
    def _path(cls, id=None):
        return '/v1/' + cls.template_name + \
               '/%s' % id if id else '/v1/' + cls.template_name

    def list(self, limit=None, marker=None, sort_key=None,
             sort_dir=None, detail=False):
        """Retrieve a list of bays.

        :param marker: Optional, the UUID of a bay, eg the last
                       bay from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of bays to return.
            2) limit == 0, return the entire list of bays.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Magnum API
               (see Magnum's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about bays.

        :returns: A list of bays.

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
            return self._list(self._path(path), self.__class__.template_name)
        else:
            return self._list_pagination(self._path(path),
                                         self.__class__.template_name,
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

    def update(self, id, patch, rollback=False):
        url = self._path(id)
        if rollback:
            url += '/?rollback=True'
        return self._update(url, patch)
