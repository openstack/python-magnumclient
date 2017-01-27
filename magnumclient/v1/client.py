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

from keystoneauth1.exceptions import catalog
from keystoneauth1 import session as ksa_session
import os_client_config
from oslo_utils import importutils

from magnumclient.common import httpclient
from magnumclient.v1 import baymodels
from magnumclient.v1 import bays
from magnumclient.v1 import certificates
from magnumclient.v1 import cluster_templates
from magnumclient.v1 import clusters
from magnumclient.v1 import mservices
from magnumclient.v1 import quotas
from magnumclient.v1 import stats

profiler = importutils.try_import("osprofiler.profiler")


DEFAULT_SERVICE_TYPE = 'container-infra'
LEGACY_DEFAULT_SERVICE_TYPE = 'container'


def _load_session(cloud=None, insecure=False, timeout=None, **kwargs):
    cloud_config = os_client_config.OpenStackConfig()
    cloud_config = cloud_config.get_one_cloud(
        cloud=cloud,
        verify=not insecure,
        **kwargs)
    verify, cert = cloud_config.get_requests_verify_args()

    auth = cloud_config.get_auth()
    session = ksa_session.Session(
        auth=auth, verify=verify, cert=cert,
        timeout=timeout)

    return session


def _load_service_type(session,
                       service_type=None, service_name=None,
                       interface=None, region_name=None):
    try:
        # Trigger an auth error so that we can throw the exception
        # we always have
        session.get_endpoint(
            service_type=service_type,
            service_name=service_name,
            interface=interface,
            region_name=region_name)
    except catalog.EndpointNotFound:
        service_type = LEGACY_DEFAULT_SERVICE_TYPE
        try:
            session.get_endpoint(
                service_type=service_type,
                service_name=service_name,
                interface=interface,
                region_name=region_name)
        except Exception as e:
            raise RuntimeError(str(e))
    except Exception as e:
        raise RuntimeError(str(e))

    return service_type


def _load_session_client(session=None, endpoint_override=None, username=None,
                         project_id=None, project_name=None,
                         auth_url=None, password=None, auth_type=None,
                         insecure=None, user_domain_id=None,
                         user_domain_name=None, project_domain_id=None,
                         project_domain_name=None, auth_token=None,
                         timeout=None, service_type=None, service_name=None,
                         interface=None, region_name=None, api_version=None,
                         **kwargs):
    if not session:
        session = _load_session(
            username=username,
            project_id=project_id,
            project_name=project_name,
            auth_url=auth_url,
            password=password,
            auth_type=auth_type,
            insecure=insecure,
            user_domain_id=user_domain_id,
            user_domain_name=user_domain_name,
            project_domain_id=project_domain_id,
            project_domain_name=project_domain_name,
            auth_token=auth_token,
            timeout=timeout,
            **kwargs
        )

    if not endpoint_override:
        service_type = _load_service_type(
            session,
            service_type=service_type,
            service_name=service_name,
            interface=interface,
            region_name=region_name,
        )

    return httpclient.SessionClient(
        service_type=service_type,
        service_name=service_name,
        interface=interface,
        region_name=region_name,
        session=session,
        endpoint_override=endpoint_override,
        api_version=api_version,
    )


class Client(object):
    def __init__(self, username=None, api_key=None, project_id=None,
                 project_name=None, auth_url=None, magnum_url=None,
                 endpoint_type=None, endpoint_override=None,
                 service_type=DEFAULT_SERVICE_TYPE,
                 region_name=None, input_auth_token=None,
                 session=None, password=None, auth_type='password',
                 interface=None, service_name=None, insecure=False,
                 user_domain_id=None, user_domain_name=None,
                 project_domain_id=None, project_domain_name=None,
                 auth_token=None, timeout=600, api_version=None,
                 **kwargs):

        # We have to keep the api_key are for backwards compat, but let's
        # remove it from the rest of our code since it's not a keystone
        # concept
        if not password:
            password = api_key
        # Backwards compat for people assing in input_auth_token
        if input_auth_token:
            auth_token = input_auth_token
        # Backwards compat for people assing in endpoint_type
        if endpoint_type:
            interface = endpoint_type

        # osc sometimes give 'None' value
        if not interface:
            interface = 'public'

        if interface.endswith('URL'):
            interface = interface[:-3]

        # fix (yolanda): os-cloud-config is using endpoint_override
        # instead of magnum_url
        if magnum_url and not endpoint_override:
            endpoint_override = magnum_url

        if endpoint_override and auth_token:
            self.http_client = httpclient.HTTPClient(
                endpoint_override,
                token=auth_token,
                api_version=api_version,
                timeout=timeout,
                insecure=insecure,
                **kwargs
            )
        else:
            self.http_client = _load_session_client(
                session=session,
                endpoint_override=endpoint_override,
                username=username,
                project_id=project_id,
                project_name=project_name,
                auth_url=auth_url,
                password=password,
                auth_type=auth_type,
                insecure=insecure,
                user_domain_id=user_domain_id,
                user_domain_name=user_domain_name,
                project_domain_id=project_domain_id,
                project_domain_name=project_domain_name,
                auth_token=auth_token,
                timeout=timeout,
                service_type=service_type,
                service_name=service_name,
                interface=interface,
                region_name=region_name,
                api_version=api_version,
                **kwargs
            )

        self.bays = bays.BayManager(self.http_client)
        self.clusters = clusters.ClusterManager(self.http_client)
        self.certificates = certificates.CertificateManager(self.http_client)
        self.baymodels = baymodels.BayModelManager(self.http_client)
        self.cluster_templates = \
            cluster_templates.ClusterTemplateManager(self.http_client)
        self.mservices = mservices.MServiceManager(self.http_client)

        profile = kwargs.pop("profile", None)
        if profiler and profile:
            # Initialize the root of the future trace: the created trace ID
            # will be used as the very first parent to which all related
            # traces will be bound to. The given HMAC key must correspond to
            # the one set in magnum-api magnum.conf, otherwise the latter
            # will fail to check the request signature and will skip
            # initialization of osprofiler on the server side.
            profiler.init(profile)
        self.stats = stats.StatsManager(self.http_client)
        self.quotas = quotas.QuotasManager(self.http_client)
