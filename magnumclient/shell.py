# Copyright 2014
# The Cloudscaling Group, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


###
# This code is taken from python-novaclient. Goal is minimal modification.
###

"""
Command-line interface to the OpenStack Magnum API.
"""

from __future__ import print_function
import argparse
import getpass
import logging
import os
import sys

from oslo_utils import encodeutils
from oslo_utils import strutils
import six

HAS_KEYRING = False
all_errors = ValueError
try:
    import keyring
    HAS_KEYRING = True
    try:
        if isinstance(keyring.get_keyring(), keyring.backend.GnomeKeyring):
            import gnomekeyring
            all_errors = (ValueError,
                          gnomekeyring.IOError,
                          gnomekeyring.NoKeyringDaemonError)
    except Exception:
        pass
except ImportError:
    pass

from magnumclient import exceptions as exc
from magnumclient.openstack.common.apiclient import auth
from magnumclient.openstack.common import cliutils
from magnumclient.v1 import client as client_v1
from magnumclient.v1 import shell as shell_v1
from magnumclient import version

DEFAULT_API_VERSION = '1'
DEFAULT_ENDPOINT_TYPE = 'publicURL'
DEFAULT_SERVICE_TYPE = 'container'

logger = logging.getLogger(__name__)


def positive_non_zero_float(text):
    if text is None:
        return None
    try:
        value = float(text)
    except ValueError:
        msg = "%s must be a float" % text
        raise argparse.ArgumentTypeError(msg)
    if value <= 0:
        msg = "%s must be greater than 0" % text
        raise argparse.ArgumentTypeError(msg)
    return value


class SecretsHelper(object):
    def __init__(self, args, client):
        self.args = args
        self.client = client
        self.key = None

    def _validate_string(self, text):
        if text is None or len(text) == 0:
            return False
        return True

    def _make_key(self):
        if self.key is not None:
            return self.key
        keys = [
            self.client.auth_url,
            self.client.projectid,
            self.client.user,
            self.client.region_name,
            self.client.endpoint_type,
            self.client.service_type,
            self.client.service_name,
            self.client.volume_service_name,
        ]
        for (index, key) in enumerate(keys):
            if key is None:
                keys[index] = '?'
            else:
                keys[index] = str(keys[index])
        self.key = "/".join(keys)
        return self.key

    def _prompt_password(self, verify=True):
        pw = None
        if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
            # Check for Ctl-D
            try:
                while True:
                    pw1 = getpass.getpass('OS Password: ')
                    if verify:
                        pw2 = getpass.getpass('Please verify: ')
                    else:
                        pw2 = pw1
                    if pw1 == pw2 and self._validate_string(pw1):
                        pw = pw1
                        break
            except EOFError:
                pass
        return pw

    def save(self, auth_token, management_url, tenant_id):
        if not HAS_KEYRING or not self.args.os_cache:
            return
        if (auth_token == self.auth_token and
           management_url == self.management_url):
            # Nothing changed....
            return
        if not all([management_url, auth_token, tenant_id]):
            raise ValueError("Unable to save empty management url/auth token")
        value = "|".join([str(auth_token),
                          str(management_url),
                          str(tenant_id)])
        keyring.set_password("magnumclient_auth", self._make_key(), value)

    @property
    def password(self):
        if self._validate_string(self.args.os_password):
            return self.args.os_password
        verify_pass = (
            strutils.bool_from_string(cliutils.env("OS_VERIFY_PASSWORD"))
        )
        return self._prompt_password(verify_pass)

    @property
    def management_url(self):
        if not HAS_KEYRING or not self.args.os_cache:
            return None
        management_url = None
        try:
            block = keyring.get_password('magnumclient_auth',
                                         self._make_key())
            if block:
                _token, management_url, _tenant_id = block.split('|', 2)
        except all_errors:
            pass
        return management_url

    @property
    def auth_token(self):
        # Now is where it gets complicated since we
        # want to look into the keyring module, if it
        # exists and see if anything was provided in that
        # file that we can use.
        if not HAS_KEYRING or not self.args.os_cache:
            return None
        token = None
        try:
            block = keyring.get_password('magnumclient_auth',
                                         self._make_key())
            if block:
                token, _management_url, _tenant_id = block.split('|', 2)
        except all_errors:
            pass
        return token

    @property
    def tenant_id(self):
        if not HAS_KEYRING or not self.args.os_cache:
            return None
        tenant_id = None
        try:
            block = keyring.get_password('magnumclient_auth',
                                         self._make_key())
            if block:
                _token, _management_url, tenant_id = block.split('|', 2)
        except all_errors:
            pass
        return tenant_id


class MagnumClientArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(MagnumClientArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        # FIXME(lzyeval): if changes occur in argparse.ArgParser._check_value
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2, "error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                     " for more information.\n" %
                     {'errmsg': message.split(choose_from)[0],
                      'mainp': progparts[0],
                      'subp': progparts[2]})


class OpenStackMagnumShell(object):

    def get_base_parser(self):
        parser = MagnumClientArgumentParser(
            prog='magnum',
            description=__doc__.strip(),
            epilog='See "magnum help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
            formatter_class=OpenStackHelpFormatter,
        )

        # Global arguments
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument('--version',
                            action='version',
                            version=version.version_info.version_string())

        parser.add_argument('--debug',
                            default=False,
                            action='store_true',
                            help="Print debugging output.")

        parser.add_argument('--os-cache',
                            default=strutils.bool_from_string(
                                cliutils.env('OS_CACHE', default=False)),
                            action='store_true',
                            help="Use the auth token cache. Defaults to False "
                            "if env[OS_CACHE] is not set.")

        parser.add_argument('--os-region-name',
                            metavar='<region-name>',
                            default=os.environ.get('OS_REGION_NAME'),
                            help='Region name. Default=env[OS_REGION_NAME].')


# TODO(mattf) - add get_timings support to Client
#        parser.add_argument('--timings',
#            default=False,
#            action='store_true',
#            help="Print call timing info")

# TODO(mattf) - use timeout
#        parser.add_argument('--timeout',
#            default=600,
#            metavar='<seconds>',
#            type=positive_non_zero_float,
#            help="Set HTTP call timeout (in seconds)")

        parser.add_argument('--os-tenant-id',
                            metavar='<auth-tenant-id>',
                            default=cliutils.env('OS_TENANT_ID'),
                            help='Defaults to env[OS_TENANT_ID].')

        parser.add_argument('--service-type',
                            metavar='<service-type>',
                            help='Defaults to container for all '
                                 'actions.')
        parser.add_argument('--service_type',
                            help=argparse.SUPPRESS)

        parser.add_argument('--endpoint-type',
                            metavar='<endpoint-type>',
                            default=cliutils.env(
                                'OS_ENDPOINT_TYPE',
                                default=DEFAULT_ENDPOINT_TYPE),
                            help='Defaults to env[OS_ENDPOINT_TYPE] or '
                            + DEFAULT_ENDPOINT_TYPE + '.')
        # NOTE(dtroyer): We can't add --endpoint_type here due to argparse
        #                thinking usage-list --end is ambiguous; but it
        #                works fine with only --endpoint-type present
        #                Go figure.  I'm leaving this here for doc purposes.
        # parser.add_argument('--endpoint_type',
        #    help=argparse.SUPPRESS)

        parser.add_argument('--magnum-api-version',
                            metavar='<magnum-api-ver>',
                            default=cliutils.env(
                                'MAGNUM_API_VERSION',
                                default=DEFAULT_API_VERSION),
                            help='Accepts "api", '
                                 'defaults to env[MAGNUM_API_VERSION].')
        parser.add_argument('--magnum_api_version',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-cacert',
                            metavar='<ca-certificate>',
                            default=cliutils.env('OS_CACERT', default=None),
                            help='Specify a CA bundle file to use in '
                            'verifying a TLS (https) server certificate. '
                            'Defaults to env[OS_CACERT].')

        parser.add_argument('--bypass-url',
                            metavar='<bypass-url>',
                            default=cliutils.env('BYPASS_URL', default=None),
                            dest='bypass_url',
                            help="Use this API endpoint instead of the "
                            "Service Catalog.")
        parser.add_argument('--bypass_url',
                            help=argparse.SUPPRESS)

        # The auth-system-plugins might require some extra options
        auth.load_auth_system_opts(parser)

        return parser

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        try:
            actions_modules = {
                '1': shell_v1.COMMAND_MODULES,
            }[version]
        except KeyError:
            actions_modules = shell_v1.COMMAND_MODULES

        for actions_module in actions_modules:
            self._find_actions(subparsers, actions_module)
        self._find_actions(subparsers, self)

        self._add_bash_completion_subparser(subparsers)

        return parser

    def _add_bash_completion_subparser(self, subparsers):
        subparser = (
            subparsers.add_parser('bash_completion',
                                  add_help=False,
                                  formatter_class=OpenStackHelpFormatter)
        )
        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hyphen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            action_help = desc.strip()
            arguments = getattr(callback, 'arguments', [])

            subparser = (
                subparsers.add_parser(command,
                                      help=action_help,
                                      description=desc,
                                      add_help=False,
                                      formatter_class=OpenStackHelpFormatter)
            )
            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS,)
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def setup_debugging(self, debug):
        if debug:
            streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
            # Set up the root logger to debug so that the submodules can
            # print debug messages
            logging.basicConfig(level=logging.DEBUG,
                                format=streamformat)
        else:
            streamformat = "%(levelname)s %(message)s"
            logging.basicConfig(level=logging.CRITICAL,
                                format=streamformat)

    def main(self, argv):

        # NOTE(Christoph Jansen): With Python 3.4 argv somehow becomes a Map.
        #                         This hack fixes it.
        argv = list(argv)

        # Parse args once to find version and debug settings
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self.setup_debugging(options.debug)

        # NOTE(dtroyer): Hackery to handle --endpoint_type due to argparse
        #                thinking usage-list --end is ambiguous; but it
        #                works fine with only --endpoint-type present
        #                Go figure.
        if '--endpoint_type' in argv:
            spot = argv.index('--endpoint_type')
            argv[spot] = '--endpoint-type'

        subcommand_parser = (
            self.get_subcommand_parser(options.magnum_api_version)
        )
        self.parser = subcommand_parser

        if options.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)

        # Short-circuit and deal with help right away.
        # NOTE(jamespage): args.func is not guaranteed with python >= 3.4
        if not hasattr(args, 'func') or args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        (os_username, os_tenant_name, os_tenant_id,
         os_auth_url, os_auth_system, endpoint_type,
         service_type, bypass_url) = (
            (args.os_username, args.os_tenant_name, args.os_tenant_id,
             args.os_auth_url, args.os_auth_system, args.endpoint_type,
             args.service_type, args.bypass_url)
        )

        if os_auth_system and os_auth_system != "keystone":
            auth_plugin = auth.load_plugin(os_auth_system)
        else:
            auth_plugin = None

        # Fetched and set later as needed
        os_password = None

        if not endpoint_type:
            endpoint_type = DEFAULT_ENDPOINT_TYPE

        if not service_type:
            service_type = DEFAULT_SERVICE_TYPE
# NA - there is only one service this CLI accesses
#            service_type = utils.get_service_type(args.func) or service_type

        # FIXME(usrleon): Here should be restrict for project id same as
        # for os_username or os_password but for compatibility it is not.
        if not cliutils.isunauthenticated(args.func):
            if auth_plugin:
                auth_plugin.parse_opts(args)

            if not auth_plugin or not auth_plugin.opts:
                if not os_username:
                    raise exc.CommandError("You must provide a username "
                                           "via either --os-username or "
                                           "env[OS_USERNAME]")

            if not os_tenant_name and not os_tenant_id:
                raise exc.CommandError("You must provide a tenant name "
                                       "or tenant id via --os-tenant-name, "
                                       "--os-tenant-id, env[OS_TENANT_NAME] "
                                       "or env[OS_TENANT_ID]")

            if not os_auth_url:
                if os_auth_system and os_auth_system != 'keystone':
                    os_auth_url = auth_plugin.get_auth_url()

            if not os_auth_url:
                    raise exc.CommandError("You must provide an auth url "
                                           "via either --os-auth-url or "
                                           "env[OS_AUTH_URL] or specify an "
                                           "auth_system which defines a "
                                           "default url with --os-auth-system "
                                           "or env[OS_AUTH_SYSTEM]")

# NOTE: The Magnum client authenticates when you create it. So instead of
#       creating here and authenticating later, which is what the novaclient
#       does, we just create the client later.

        # Now check for the password/token of which pieces of the
        # identifying keyring key can come from the underlying client
        if not cliutils.isunauthenticated(args.func):
            # NA - Client can't be used with SecretsHelper
            if (auth_plugin and auth_plugin.opts and
                    "os_password" not in auth_plugin.opts):
                use_pw = False
            else:
                use_pw = True

            if use_pw:
                # Auth using token must have failed or not happened
                # at all, so now switch to password mode and save
                # the token when its gotten... using our keyring
                # saver
                os_password = args.os_password
                if not os_password:
                    raise exc.CommandError(
                        'Expecting a password provided via either '
                        '--os-password, env[OS_PASSWORD], or '
                        'prompted response')

        try:
            client = {
                '1': client_v1,
            }[options.magnum_api_version]
        except KeyError:
            client = client_v1

        self.cs = client.Client(username=os_username,
                                api_key=os_password,
                                project_id=os_tenant_id,
                                project_name=os_tenant_name,
                                auth_url=os_auth_url,
                                service_type=service_type,
                                region_name=args.os_region_name,
                                magnum_url=bypass_url)

        args.func(self.cs, args)

    def _dump_timings(self, timings):
        class Tyme(object):
            def __init__(self, url, seconds):
                self.url = url
                self.seconds = seconds
        results = [Tyme(url, end - start) for url, start, end in timings]
        total = 0.0
        for tyme in results:
            total += tyme.seconds
        results.append(Tyme("Total", total))
        cliutils.print_list(results, ["url", "seconds"], sortby_index=None)

    def do_bash_completion(self, _args):
        """Prints arguments for bash-completion.

        Prints all of the commands and options to stdout so that the
        magnum.bash_completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in sc._optionals._option_string_actions.keys():
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
        print(' '.join(commands | options))

    @cliutils.arg('command', metavar='<subcommand>', nargs='?',
                  help='Display help for <subcommand>.')
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        # NOTE(jamespage): args.command is not guaranteed with python >= 3.4
        command = getattr(args, 'command', '')

        if command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()


# I'm picky about my shell help.
class OpenStackHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(OpenStackHelpFormatter, self).start_section(heading)


def main():
    try:
        OpenStackMagnumShell().main(map(encodeutils.safe_decode, sys.argv[1:]))

    except Exception as e:
        logger.debug(e, exc_info=1)
        print("ERROR: %s" % encodeutils.safe_encode(six.text_type(e)),
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
