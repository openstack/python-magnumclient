# Copyright (c) 2018 European Organization for Nuclear Research.
# All Rights Reserved.
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

from magnumclient.common import utils
from magnumclient import exceptions
from magnumclient.v1 import baseunit


CREATION_ATTRIBUTES = ['docker_volume_size', 'labels', 'flavor_id', 'image_id',
                       'project_id', 'node_count', 'name', 'role',
                       'min_node_count', 'max_node_count']


class NodeGroup(baseunit.BaseTemplate):
    template_name = "NodeGroups"


class NodeGroupManager(baseunit.BaseTemplateManager):
    resource_class = NodeGroup
    template_name = 'nodegroups'
    api_name = 'nodegroups'

    @classmethod
    def _path(cls, cluster_id, id=None):
        path = '/v1/clusters/%s/%s/' % (cluster_id, cls.template_name)
        if id:
            path += str(id)
        return path

    def list(self, cluster_id, limit=None, marker=None, sort_key=None,
             sort_dir=None, role=None, detail=False):
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(marker, limit, sort_key, sort_dir)
        path = ''
        if role:
            filters.append('role=%s' % role)
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(cluster_id, id=path),
                              self.__class__.api_name)
        else:
            return self._list_pagination(self._path(cluster_id, id=path),
                                         self.__class__.api_name,
                                         limit=limit)

    def get(self, cluster_id, id):
        try:
            return self._list(self._path(cluster_id, id=id))[0]
        except IndexError:
            return None

    def create(self, cluster_id, **kwargs):
        new = {}
        for (key, value) in kwargs.items():
            if key in CREATION_ATTRIBUTES:
                new[key] = value
            else:
                raise exceptions.InvalidAttribute(
                    "Key must be in %s" % ",".join(CREATION_ATTRIBUTES))
        return self._create(self._path(cluster_id), new)

    def delete(self, cluster_id, id):
        return self._delete(self._path(cluster_id, id=id))

    def update(self, cluster_id, id, patch):
        return self._update(self._path(cluster_id, id=id), patch)
