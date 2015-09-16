# Copyright 2015 Rackspace, Inc.  All rights reserved.
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
from magnumclient import exceptions


CREATION_ATTRIBUTES = ['bay_uuid', 'csr']


class Certificate(base.Resource):
    def __repr__(self):
        return "<Certificate %s>" % self._info


class CertificateManager(base.Manager):
    resource_class = Certificate

    @staticmethod
    def _path(id=None):
        return '/v1/certificates/%s' % id if id else '/v1/certificates'

    def get(self, bay_uuid):
        try:
            return self._list(self._path(bay_uuid))[0]
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
