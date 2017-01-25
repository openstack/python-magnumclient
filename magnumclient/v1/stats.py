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


class Stats(base.Resource):
    def __repr__(self):
        return "<Stats %s>" % self._info


class StatsManager(base.Manager):
    resource_class = Stats

    @staticmethod
    def _path(id=None):
        return '/v1/stats?project_id=%s' % id if id else '/v1/stats'

    def list(self, project_id=None):
        try:
            return self._list(self._path(project_id))[0]
        except IndexError:
            return None
