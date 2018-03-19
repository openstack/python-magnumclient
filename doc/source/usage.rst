===========================================
Python bindings to the OpenStack Magnum API
===========================================

This is a client for the OpenStack Magnum API. It includes a Python
API (the :mod:`magnumclient` module) and a command-line script
(installed as :program:`magnum`).

Python API
==========

To use python-magnumclient in a project, create a client instance
using the keystoneauth session API::

    from keystoneauth1.identity import v3
    from keystoneauth1 import session
    from keystoneclient.v3 import client

    from magnumclient.client import Client

    magnum_endpoint = "http://magnum.example.com:9511/v1"

    auth = v3.Password(auth_url='http://my.keystone.com:5000/v3',
                       username='myuser',
                       password='mypassword',
                       project_name='myproject',
                       user_domain_id='default',
                       project_domain_id='default')
    sess = session.Session(auth=auth)

    magnum = Client('1', endpoint_override=magnum_endpoint, session=sess)
    magnum.clusters.list()

For more information on keystoneauth API, see `Using Sessions`_.

.. _Using Sessions: https://docs.openstack.org/keystoneauth/latest/using-sessions.html

Command-line tool
=================

In order to use the CLI, you must provide your OpenStack username,
password, project name, user domain ID, project domain ID, and auth
endpoint. Use the corresponding configuration options (--os-username,
--os-password, --os-project-name, --os-project-domain-id,
--os-user-domain-id, and --os-auth-url) or set them in environment
variables::

    export OS_USERNAME=myuser
    export OS_PASSWORD=mypassword
    export OS_PROJECT_NAME=myproject
    export OS_USER_DOMAIN_ID=default
    export OS_PROJECT_DOMAIN_ID=default
    export OS_AUTH_URL=http://my.keystone.com:5000/v3

From there, all shell commands take the form::

    magnum <command> [arguments...]

Run :program:`magnum help` to see a complete listing of available
commands.  Run :program:`magnum help <command>` to get detailed help
for that command.
