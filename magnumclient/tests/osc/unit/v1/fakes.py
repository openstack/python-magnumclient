#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import argparse
import copy
import datetime
import uuid

from magnumclient.tests.osc.unit import osc_fakes
from magnumclient.tests.osc.unit import osc_utils


class FakeBaseModel(object):
    def __repr__(self):
        return "<" + self.__class__.model_name + "%s>" % self._info


class FakeBaseModelManager(object):
    def list(self, limit=None, marker=None, sort_key=None,
             sort_dir=None, detail=False):
        pass

    def get(self, id):
        pass

    def create(self, **kwargs):
        pass

    def delete(self, id):
        pass

    def update(self, id, patch):
        pass

    def rotate_ca(self, **kwargs):
        pass


class FakeStatsModelManager(object):
    def list(self, **kwargs):
        pass


class FakeQuotasModelManager(object):
    def get(self, id, resource):
        pass

    def create(self, **kwargs):
        pass

    def delete(self, id):
        pass


class FakeNodeGroupManager(object):
    def list(self, cluster_id, limit=None, marker=None, sort_key=None,
             sort_dir=None, detail=False):
        pass

    def get(self, cluster_id, id):
        pass

    def create(self, cluster_id, **kwargs):
        pass

    def delete(self, cluster_id, id):
        pass

    def update(self, cluster_id, id, patch):
        pass


class FakeCertificatesModelManager(FakeBaseModelManager):
    def get(self, cluster_uuid):
        pass


class MagnumFakeContainerInfra(object):
    def __init__(self):
        self.cluster_templates = FakeBaseModelManager()
        self.clusters = FakeBaseModelManager()
        self.mservices = FakeBaseModelManager()
        self.certificates = FakeCertificatesModelManager()
        self.stats = FakeStatsModelManager()
        self.quotas = FakeQuotasModelManager()
        self.nodegroups = FakeNodeGroupManager()


class MagnumFakeClientManager(osc_fakes.FakeClientManager):
    def __init__(self):
        super(MagnumFakeClientManager, self).__init__()
        self.container_infra = MagnumFakeContainerInfra()


class MagnumParseException(Exception):
    """The base exception class for all exceptions this library raises."""

    def __init__(self, message=None, details=None):
        self.message = message or "Argument parse exception"
        self.details = details or None

    def __str__(self):
        return self.message


class TestMagnumClientOSCV1(osc_utils.TestCase):

    def setUp(self):
        super(TestMagnumClientOSCV1, self).setUp()
        self.fake_stdout = osc_fakes.FakeStdout()
        self.fake_log = osc_fakes.FakeLog()
        self.app = osc_fakes.FakeApp(self.fake_stdout, self.fake_log)
        self.namespace = argparse.Namespace()
        self.app.client_manager = MagnumFakeClientManager()

    def check_parser(self, cmd, args, verify_args):
        cmd_parser = cmd.get_parser('check_parser')
        try:
            parsed_args = cmd_parser.parse_args(args)
        except SystemExit:
            raise MagnumParseException()
        for av in verify_args:
            attr, value = av
            if attr:
                self.assertIn(attr, parsed_args)
                self.assertEqual(value, getattr(parsed_args, attr))
        return parsed_args


class FakeClusterTemplate(object):
    """Fake one or more ClusterTemplate."""

    @staticmethod
    def create_one_cluster_template(attrs=None):
        """Create a fake ClusterTemplate.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with flavor_id, image_id, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        ct_info = {
            'links': [],
            'insecure_registry': None,
            'labels': None,
            'updated_at': None,
            'floating_ip_enabled': True,
            'fixed_subnet': None,
            'master_flavor_id': None,
            'uuid': uuid.uuid4().hex,
            'no_proxy': None,
            'https_proxy': None,
            'tls_disabled': False,
            'keypair_id': None,
            'public': False,
            'http_proxy': None,
            'docker_volume_size': None,
            'server_type': 'vm',
            'external_network_id': 'public',
            'cluster_distro': 'fedora-atomic',
            'image_id': 'fedora-atomic-latest',
            'volume_driver': None,
            'registry_enabled': False,
            'docker_storage_driver': 'devicemapper',
            'apiserver_port': None,
            'name': 'fake-ct-' + uuid.uuid4().hex,
            'created_at': datetime.datetime.now(),
            'network_driver': 'flannel',
            'fixed_network': None,
            'coe': 'kubernetes',
            'flavor_id': 'm1.medium',
            'master_lb_enabled': False,
            'dns_nameserver': '8.8.8.8',
            'hidden': False
        }

        # Overwrite default attributes.
        ct_info.update(attrs)

        ct = osc_fakes.FakeResource(info=copy.deepcopy(ct_info), loaded=True)
        return ct

    @staticmethod
    def create_cluster_templates(attrs=None, count=2):
        """Create multiple fake cluster templates.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of cluster templates to fake
        :return:
            A list of FakeResource objects faking the cluster templates
        """
        cts = []
        for i in range(0, count):
            cts.append(FakeClusterTemplate.create_one_cluster_template(attrs))

        return cts


class FakeCluster(object):
    """Fake one or more Cluster."""

    @staticmethod
    def create_one_cluster(attrs=None):
        """Create a fake Cluster.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with flavor_id, image_id, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        cluster_info = {
            'status': 'CREATE_IN_PROGRESS',
            'health_status': 'HEALTHY',
            'cluster_template_id': 'fake-ct',
            'node_addresses': [],
            'uuid': '3a369884-b6ba-484f-a206-919b4b718aff',
            'stack_id': 'c4554582-77bd-4734-8f1a-72c3c40e5fb4',
            'status_reason': None,
            'labels': {},
            'created_at': '2017-03-16T18:40:39+00:00',
            'updated_at': '2017-03-16T18:40:45+00:00',
            'coe_version': None,
            'faults': None,
            'keypair': 'fakekey',
            'api_address': None,
            'master_addresses': [],
            'create_timeout': 60,
            'node_count': 1,
            'discovery_url': 'https://fake.cluster',
            'master_count': 1,
            'container_version': None,
            'name': 'fake-cluster',
            'master_flavor_id': None,
            'flavor_id': 'm1.medium',
            'project_id': None,
            'health_status_reason': {'api': 'ok'}
        }

        # Overwrite default attributes.
        cluster_info.update(attrs)

        cluster = osc_fakes.FakeResource(info=copy.deepcopy(cluster_info),
                                         loaded=True)
        return cluster


class FakeCert(object):
    def __init__(self, pem):
        self.pem = pem


class FakeQuota(object):
    """Fake one or more Quota"""

    @staticmethod
    def create_one_quota(attrs=None):
        """Create a fake quota

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with project_id, resource and so on
        """

        attrs = attrs or {}

        quota_info = {
            'resource': 'Cluster',
            'created_at': '2017-09-15T05:40:34+00:00',
            'updated_at': '2017-09-15T05:40:34+00:00',
            'hard_limit': 1,
            'project_id': 'be24b6fba2ed4476b2bd01fa8f0ba74e',
            'id': 10,
            'name': 'fake-quota',
        }

        quota_info.update(attrs)
        quota = osc_fakes.FakeResource(info=copy.deepcopy(quota_info),
                                       loaded=True)
        return quota


class FakeNodeGroup(object):
    """Fake one or more NodeGroup."""

    @staticmethod
    def create_one_nodegroup(attrs=None):
        """Create a fake NodeGroup.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with flavor_id, image_id, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        nodegroup_info = {
            'created_at': '2017-03-16T18:40:39+00:00',
            'updated_at': '2017-03-16T18:40:45+00:00',
            'uuid': '3a369884-b6ba-484f-a206-919b4b718aff',
            'cluster_id': 'fake-cluster',
            'docker_volume_size': None,
            'node_addresses': [],
            'labels': {},
            'node_count': 1,
            'name': 'fake-nodegroup',
            'flavor_id': 'm1.medium',
            'image_id': 'fedora-latest',
            'project_id': None,
            'role': 'worker',
            'max_node_count': 10,
            'min_node_count': 1,
            'is_default': False,
            'stack_id': '3a369884-b6ba-484f-fake-stackb718aff',
            'status': 'CREATE_COMPLETE',
            'status_reason': 'None'
        }

        # Overwrite default attributes.
        nodegroup_info.update(attrs)

        nodegroup = osc_fakes.FakeResource(info=copy.deepcopy(nodegroup_info),
                                           loaded=True)
        return nodegroup
