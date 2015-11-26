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


CREATION_ATTRIBUTES = ['bay_uuid', 'manifest', 'manifest_url']


class Pod(base.Resource):
    def __repr__(self):
        return "<Pod %s>" % self._info


class PodManager(base.Manager):
    resource_class = Pod

    @staticmethod
    def _path(id=None, bay_ident=None):
        if id and bay_ident:
            return '/v1/pods/%s/?bay_ident=%s' % (id, bay_ident)
        elif bay_ident:
            return '/v1/pods/?bay_ident=%s' % (bay_ident)
        else:
            return '/v1/pods'

    def list(self, bay_ident, limit=None, marker=None, sort_key=None,
             sort_dir=None, detail=False):
        """Retrieve a list of pods.

        :param bay_ident: UUID or Name of the Bay.
        :param marker: Optional, the UUID or Name of a pod, e.g. the last
                       pod from a previous result set. Return the next
                       result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of pods to return.
            2) limit == 0, return the entire list of pods.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Magnum API
               (see Magnum's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed
                       information about pods.

        :returns: A list of pods.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(marker, limit, sort_key, sort_dir)
        filters.append('bay_ident=%s' % bay_ident)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(bay_ident=bay_ident), "pods")
        else:
            return self._list_pagination(self._path(bay_ident=bay_ident),
                                         "pods", limit=limit)

    def get(self, id, bay_ident):
        try:
            return self._list(self._path(id, bay_ident))[0]
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

    def delete(self, id, bay_ident):
        return self._delete(self._path(id, bay_ident))

    def update(self, id, bay_ident, patch):
        return self._update(self._path(id, bay_ident), patch)
