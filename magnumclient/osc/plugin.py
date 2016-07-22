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

import logging

from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = 'os_container_infra_api_version'
API_NAME = 'container_infra'
API_VERSIONS = {
    '1': 'magnumclient.v1.client.Client',
}


def make_client(instance):
    """Returns a magnum client."""
    magnum_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating magnum client: %s', magnum_client)

    client = magnum_client(session=instance.session,
                           region_name=instance._region_name,
                           interface=instance._interface,
                           insecure=instance._insecure,
                           ca_cert=instance._cacert)
    return client


def build_option_parser(parser):
    """Hook to add global options"""

    parser.add_argument(
        '--os-container-infra-api-version',
        metavar='<container-infra-api-version>',
        default=utils.env(
            'OS_CONTAINER_INFRA_API_VERSION',
            default=DEFAULT_API_VERSION),
        help='Container-Infra API version, default=' +
             DEFAULT_API_VERSION +
             ' (Env: OS_CONTAINER_INFRA_API_VERSION)')
    return parser
