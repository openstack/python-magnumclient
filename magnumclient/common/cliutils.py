# Copyright 2012 Red Hat, Inc.
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

# W0603: Using the global statement
# W0621: Redefining name %s from outer scope
# pylint: disable=W0603,W0621

from __future__ import print_function

import getpass
import inspect
import os
import sys
import textwrap

import decorator
from magnumclient.common.apiclient import exceptions
from oslo_utils import encodeutils
from oslo_utils import strutils
import prettytable
import six
from six import moves

from magnumclient.i18n import _


NAME_DEPRECATION_BASE = ('%sThe --name parameter is deprecated and '
                         'will be removed in a future release. Use the '
                         '<name> positional parameter %s.')

NAME_DEPRECATION_HELP = NAME_DEPRECATION_BASE % ('', 'instead')

NAME_DEPRECATION_WARNING = NAME_DEPRECATION_BASE % (
    'WARNING: ', 'to avoid seeing this message')


def deprecation_message(preamble, new_name):
    msg = ('%s This parameter is deprecated and will be removed in a future '
           'release. Use --%s instead.' % (preamble, new_name))
    return msg


class MissingArgs(Exception):
    """Supplied arguments are not sufficient for calling a function."""
    def __init__(self, missing):
        self.missing = missing
        msg = _("Missing arguments: %s") % ", ".join(missing)
        super(MissingArgs, self).__init__(msg)


class DuplicateArgs(Exception):
    """More than one of the same argument type was passed."""
    def __init__(self, param, dupes):
        msg = _('Duplicate "%(param)s" arguments: %(dupes)s') % {
            'param': param, 'dupes': ", ".join(dupes)}
        super(DuplicateArgs, self).__init__(msg)


def validate_args(fn, *args, **kwargs):
    """Check that the supplied args are sufficient for calling a function.

    >>> validate_args(lambda a: None)
    Traceback (most recent call last):
        ...
    MissingArgs: Missing argument(s): a
    >>> validate_args(lambda a, b, c, d: None, 0, c=1)
    Traceback (most recent call last):
        ...
    MissingArgs: Missing argument(s): b, d

    :param fn: the function to check
    :param arg: the positional arguments supplied
    :param kwargs: the keyword arguments supplied
    """
    argspec = inspect.getargspec(fn)

    num_defaults = len(argspec.defaults or [])
    required_args = argspec.args[:len(argspec.args) - num_defaults]

    def isbound(method):
        return getattr(method, '__self__', None) is not None

    if isbound(fn):
        required_args.pop(0)

    missing = [arg for arg in required_args if arg not in kwargs]
    missing = missing[len(args):]
    if missing:
        raise MissingArgs(missing)


def validate_name_args(positional_name, optional_name):
    if optional_name:
        print(NAME_DEPRECATION_WARNING)
    if positional_name and optional_name:
        raise DuplicateArgs("<name>", (positional_name, optional_name))


def deprecated(message):
    """Decorator for marking a call as deprecated by printing a given message.

    Example:
    >>> @deprecated("Bay functions are deprecated and should be replaced by "
    ...             "calls to cluster")
    ... def bay_create(args):
    ...     pass
    """
    @decorator.decorator
    def wrapper(func, *args, **kwargs):
        print(message)
        return func(*args, **kwargs)
    return wrapper


def deprecation_map(dep_map):
    """Decorator for applying a map of deprecating arguments to a function.

    The map connects deprecating arguments and their replacements. The
    shell.py script uses this map to create mutually exclusive argument groups
    in argparse and also prints a deprecation warning telling the user to
    switch to the updated argument.

    NOTE: This decorator MUST be the outermost in the chain of argument
    decorators to work correctly.

    Example usage:
    >>> @deprecation_map({ "old-argument": "new-argument" })
    ... @args("old-argument", required=True)
    ... @args("new-argument", required=True)
    ... def do_command_line_stuff():
    ...     pass
    """
    def _decorator(func):
        if not hasattr(func, 'arguments'):
            return func

        func.deprecated_groups = []
        for old_param, new_param in dep_map.items():
            old_info, new_info = None, None
            required = False
            for (args, kwargs) in func.arguments:
                if old_param in args:
                    old_info = (args, kwargs)
                    # Old arguments shouldn't be required if they were not
                    # previously, so prioritize old requirement
                    if 'required' in kwargs:
                        required = kwargs['required']
                    # Set to false so argparse doesn't get angry
                    kwargs['required'] = False
                elif new_param in args:
                    new_info = (args, kwargs)
                    kwargs['required'] = False
                if old_info and new_info:
                    break
            # Add a tuple of (old, new, required), which in turn is:
            # ((old_args, old_kwargs), (new_args, new_kwargs), required)
            func.deprecated_groups.append((old_info, new_info, required))
            # Remove arguments that would be duplicated by the groups we made
            func.arguments.remove(old_info)
            func.arguments.remove(new_info)

        return func
    return _decorator


def arg(*args, **kwargs):
    """Decorator for CLI args.

    Example:

    >>> @arg("name", help="Name of the new entity")
    ... def entity_create(args):
    ...     pass
    """
    def _decorator(func):
        add_arg(func, *args, **kwargs)
        return func
    return _decorator


def env(*args, **kwargs):
    """Returns the first environment variable set.

    If all are empty, defaults to '' or keyword arg `default`.
    """
    for arg in args:
        value = os.environ.get(arg)
        if value:
            return value
    return kwargs.get('default', '')


def add_arg(func, *args, **kwargs):
    """Bind CLI arguments to a shell.py `do_foo` function."""

    if not hasattr(func, 'arguments'):
        func.arguments = []

    # NOTE(sirp): avoid dups that can occur when the module is shared across
    # tests.
    if (args, kwargs) not in func.arguments:
        # Because of the semantics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.arguments.insert(0, (args, kwargs))


def unauthenticated(func):
    """Adds 'unauthenticated' attribute to decorated function.

    Usage:

    >>> @unauthenticated
    ... def mymethod(f):
    ...     pass
    """
    func.unauthenticated = True
    return func


def isunauthenticated(func):
    """Checks if the function does not require authentication.

    Mark such functions with the `@unauthenticated` decorator.

    :returns: bool
    """
    return getattr(func, 'unauthenticated', False)


def print_list(objs, fields, formatters=None, sortby_index=0,
               mixed_case_fields=None, field_labels=None):
    """Print a list or objects as a table, one row per object.

    :param objs: iterable of :class:`Resource`
    :param fields: attributes that correspond to columns, in order
    :param formatters: `dict` of callables for field formatting
    :param sortby_index: index of the field for sorting table rows
    :param mixed_case_fields: fields corresponding to object attributes that
        have mixed case names (e.g., 'serverId')
    :param field_labels: Labels to use in the heading of the table, default to
        fields.
    """
    formatters = formatters or {}
    mixed_case_fields = mixed_case_fields or []
    field_labels = field_labels or fields
    if len(field_labels) != len(fields):
        raise ValueError(_("Field labels list %(labels)s has different number "
                           "of elements than fields list %(fields)s"),
                         {'labels': field_labels, 'fields': fields})

    if sortby_index is None:
        kwargs = {}
    else:
        kwargs = {'sortby': field_labels[sortby_index]}
    pt = prettytable.PrettyTable(field_labels)
    pt.align = 'l'

    for o in objs:
        row = []
        for field in fields:
            data = '-'
            if field in formatters:
                data = formatters[field](o)
            else:
                if field in mixed_case_fields:
                    field_name = field.replace(' ', '_')
                else:
                    field_name = field.lower().replace(' ', '_')
                data = getattr(o, field_name, '')
            if data is None:
                data = '-'
            row.append(data)
        pt.add_row(row)

    if six.PY3:
        print(encodeutils.safe_encode(pt.get_string(**kwargs)).decode())
    else:
        print(encodeutils.safe_encode(pt.get_string(**kwargs)))


def keys_and_vals_to_strs(dictionary):
    """Recursively convert a dictionary's keys and values to strings.

    :param dictionary: dictionary whose keys/vals are to be converted to strs
    """
    def to_str(k_or_v):
        if isinstance(k_or_v, dict):
            return keys_and_vals_to_strs(k_or_v)
        elif isinstance(k_or_v, six.text_type):
            return str(k_or_v)
        else:
            return k_or_v
    return dict((to_str(k), to_str(v)) for k, v in dictionary.items())


def print_dict(dct, dict_property="Property", wrap=0):
    """Print a `dict` as a table of two columns.

    :param dct: `dict` to print
    :param dict_property: name of the first column
    :param wrap: wrapping for the second column
    """
    pt = prettytable.PrettyTable([dict_property, 'Value'])
    pt.align = 'l'
    for k, v in dct.items():
        # convert dict to str to check length
        if isinstance(v, dict):
            v = six.text_type(keys_and_vals_to_strs(v))
        if wrap > 0:
            v = textwrap.fill(six.text_type(v), wrap)
        # if value has a newline, add in multiple rows
        # e.g. fault with stacktrace
        if v and isinstance(v, six.string_types) and r'\n' in v:
            lines = v.strip().split(r'\n')
            col1 = k
            for line in lines:
                pt.add_row([col1, line])
                col1 = ''
        elif isinstance(v, list):
            val = str([str(i) for i in v])
            if val is None:
                val = '-'
            pt.add_row([k, val])
        else:
            if v is None:
                v = '-'
            pt.add_row([k, v])

    if six.PY3:
        print(encodeutils.safe_encode(pt.get_string()).decode())
    else:
        print(encodeutils.safe_encode(pt.get_string()))


def get_password(max_password_prompts=3):
    """Read password from TTY."""
    verify = strutils.bool_from_string(env("OS_VERIFY_PASSWORD"))
    pw = None
    if hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
        # Check for Ctrl-D
        try:
            for __ in moves.range(max_password_prompts):
                pw1 = getpass.getpass("OS Password: ")
                if verify:
                    pw2 = getpass.getpass("Please verify: ")
                else:
                    pw2 = pw1
                if pw1 == pw2 and pw1:
                    pw = pw1
                    break
        except EOFError:
            pass
    return pw


def service_type(stype):
    """Adds 'service_type' attribute to decorated function.

    Usage:

    .. code-block:: python

       @service_type('volume')
       def mymethod(f):
       ...
    """
    def inner(f):
        f.service_type = stype
        return f
    return inner


def get_service_type(f):
    """Retrieves service type from function."""
    return getattr(f, 'service_type', None)


def pretty_choice_list(l):
    return ', '.join("'%s'" % i for i in l)


def exit(msg=''):
    if msg:
        print(msg, file=sys.stderr)
    sys.exit(1)


def _format_field_name(attr):
    """Format an object attribute in a human-friendly way."""
    # Split at ':' and leave the extension name as-is.
    parts = attr.rsplit(':', 1)
    name = parts[-1].replace('_', ' ')
    # Don't title() on mixed case
    if name.isupper() or name.islower():
        name = name.title()
    parts[-1] = name
    return ': '.join(parts)


def make_field_formatter(attr, filters=None):
    """Given an object attribute.

    Return a formatted field name and a formatter suitable for passing to
    print_list.
    Optionally pass a dict mapping attribute names to a function. The function
    will be passed the value of the attribute and should return the string to
    display.
    """

    filter_ = None
    if filters:
        filter_ = filters.get(attr)

    def get_field(obj):
        field = getattr(obj, attr, '')
        if field and filter_:
            field = filter_(field)
        return field

    name = _format_field_name(attr)
    formatter = get_field
    return name, formatter


def _get_list_table_columns_and_formatters(fields, objs, exclude_fields=(),
                                           filters=None):
    """Check and add fields to output columns.

    If there is any value in fields that not an attribute of obj,
    CommandError will be raised.
    If fields has duplicate values (case sensitive), we will make them unique
    and ignore duplicate ones.
    :param fields: A list of string contains the fields to be printed.
    :param objs: An list of object which will be used to check if field is
                 valid or not. Note, we don't check fields if obj is None or
                 empty.
    :param exclude_fields: A tuple of string which contains the fields to be
                           excluded.
    :param filters: A dictionary defines how to get value from fields, this
                    is useful when field's value is a complex object such as
                    dictionary.
    :return: columns, formatters.
             columns is a list of string which will be used as table header.
             formatters is a dictionary specifies how to display the value
             of the field.
             They can be [], {}.
    :raise: magnumclient.common.apiclient.exceptions.CommandError.
    """

    if objs and isinstance(objs, list):
        obj = objs[0]
    else:
        obj = None
        fields = None

    columns = []
    formatters = {}

    if fields:
        non_existent_fields = []
        exclude_fields = set(exclude_fields)

        for field in fields.split(','):
            if not hasattr(obj, field):
                non_existent_fields.append(field)
                continue
            if field in exclude_fields:
                continue
            field_title, formatter = make_field_formatter(field, filters)
            columns.append(field_title)
            formatters[field_title] = formatter
            exclude_fields.add(field)

        if non_existent_fields:
            raise exceptions.CommandError(
                _("Non-existent fields are specified: %s") %
                non_existent_fields
            )
    return columns, formatters
