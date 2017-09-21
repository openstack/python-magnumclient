# Copyright 2015 NEC Corporation.  All rights reserved.
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

from magnumclient.common import cliutils as utils
from magnumclient.common import utils as magnum_utils
from magnumclient.i18n import _
from osc_lib.command import command

QUOTA_ATTRIBUTES = [
    'resource',
    'created_at',
    'updated_at',
    'hard_limit',
    'project_id',
    'id'
]


def _show_quota(quota):
    utils.print_dict(quota._info)


class CreateQuotas(command.Command):
    _description = _("Create a quota.")

    def get_parser(self, prog_name):
        parser = super(CreateQuotas, self).get_parser(prog_name)
        parser.add_argument('--project-id',
                            required=True,
                            metavar='<project-id>',
                            help='Project ID')
        parser.add_argument('--resource',
                            required=True,
                            metavar='<resource>',
                            help='Resource name.')
        parser.add_argument('--hard-limit',
                            metavar='<hard-limit>',
                            type=int,
                            default=1,
                            help='Max resource limit (default: hard-limit=1)')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra

        opts = {
            'project_id': parsed_args.project_id,
            'resource': parsed_args.resource,
            'hard_limit': parsed_args.hard_limit
        }
        try:
            quota = mag_client.quotas.create(**opts)
            _show_quota(quota)
        except Exception as e:
            print("Create quota for project_id %(id)s resource %(res)s failed:"
                  " %(e)s" % {'id': parsed_args.project_id,
                              'res': parsed_args.resource,
                              'e': e})


class DeleteQuotas(command.Command):
    _description = _("Delete specified resource quota.")

    def get_parser(self, prog_name):
        parser = super(DeleteQuotas, self).get_parser(prog_name)
        parser.add_argument('--project-id',
                            required=True,
                            metavar='<project-id>',
                            help='Project ID')
        parser.add_argument('--resource',
                            required=True,
                            metavar='<resource>',
                            help='Resource name.')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra

        try:
            mag_client.quotas.delete(parsed_args.project_id,
                                     parsed_args.resource)
            print("Request to delete quota for project id %(id)s and resource "
                  "%(res)s has been accepted." % {'id': parsed_args.project_id,
                                                  'res': parsed_args.resource})
        except Exception as e:
            print("Quota delete failed for project id %(id)s and resource "
                  "%(res)s :%(e)s" % {'id': parsed_args.project_id,
                                      'res': parsed_args.resource,
                                      'e': e})


class ShowQuotas(command.Command):
    _description = _("Show details about the given project resource quota.")

    def get_parser(self, prog_name):
        parser = super(ShowQuotas, self).get_parser(prog_name)
        parser.add_argument('--project-id',
                            required=True,
                            metavar='<project-id>',
                            help='Project ID')
        parser.add_argument('--resource',
                            required=True,
                            metavar='<resource>',
                            help='Resource name.')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra
        project_id = parsed_args.project_id
        resource = parsed_args.resource
        quota = mag_client.quotas.get(project_id, resource)
        _show_quota(quota)


class UpdateQuotas(command.Command):
    _description = _("Update information about the given "
                     "project resource quota.")

    def get_parser(self, prog_name):
        parser = super(UpdateQuotas, self).get_parser(prog_name)
        parser.add_argument('--project-id',
                            required=True,
                            metavar='<project-id>',
                            help='Project ID')
        parser.add_argument('--resource',
                            required=True,
                            metavar='<resource>',
                            help='Resource name.')
        parser.add_argument('--hard-limit',
                            metavar='<hard-limit>',
                            type=int,
                            default=1,
                            help='Max resource limit (default: hard-limit=1)')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra

        opts = {
            'project_id': parsed_args.project_id,
            'resource': parsed_args.resource,
            'hard_limit': parsed_args.hard_limit
        }
        try:
            quota = mag_client.quotas.update(parsed_args.project_id,
                                             parsed_args.resource, opts)
            _show_quota(quota)
        except Exception as e:
            print("Update quota for project_id %(id)s resource %(res)s failed:"
                  " %(e)s" % {'id': parsed_args.project_id,
                              'res': parsed_args.resource,
                              'e': e})


class ListQuotas(command.Command):
    _description = _("Print a list of available quotas.")

    def get_parser(self, prog_name):
        parser = super(ListQuotas, self).get_parser(prog_name)
        parser.add_argument('--marker',
                            metavar='<marker>',
                            default=None,
                            help=_('The last quota UUID of the previous page; '
                                   'displays list of quotas after "marker".'))
        parser.add_argument('--limit',
                            metavar='<limit>',
                            type=int,
                            help='Maximum number of quotas to return.')
        parser.add_argument('--sort-key',
                            metavar='<sort-key>',
                            help='Column to sort results by.')
        parser.add_argument('--sort-dir',
                            metavar='<sort-dir>',
                            choices=['desc', 'asc'],
                            help='Direction to sort. "asc" or "desc".')
        parser.add_argument('--all-tenants',
                            action='store_true',
                            default=False,
                            help='Flag to indicate list all tenant quotas.')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        mag_client = self.app.client_manager.container_infra

        quotas = mag_client.quotas.list(marker=parsed_args.marker,
                                        limit=parsed_args.limit,
                                        sort_key=parsed_args.sort_key,
                                        sort_dir=parsed_args.sort_dir,
                                        all_tenants=parsed_args.all_tenants)
        columns = ['project_id', 'resource', 'hard_limit']
        utils.print_list(quotas, columns,
                         {'versions':
                          magnum_utils.print_list_field('versions')},
                         sortby_index=None)
