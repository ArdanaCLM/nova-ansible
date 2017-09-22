#!/usr/bin/python
#
# (c) Copyright 2016-2017 Hewlett Packard Enterprise Development LP
# (c) Copyright 2017 SUSE LLC
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

from ansible.module_utils.basic import *  # noqa

try:
    from keystoneauth1.identity import v3
    from keystoneauth1 import session
except ImportError:
    msg = "'keysthoneauth is required for this module to work'"
    print("failed=True msg=%s" % (msg))

try:
    from novaclient import client as nova_client
except ImportError:
    print("failed=True msg='novaclient is required for this module to work'")

DOCUMENTATION = '''
---
module: create_flavor
version_added: "1.0"
short_description: Create a given Nova flavor
description:
   - Create a given Nova flavor for a given region.
options:
   login_username:
     description:
        - login username to authenticate to keystone
     required: true
     default: admin
   login_password:
     description:
        - Password of login user
     required: true
     default: 'yes'
   login_tenant_name:
     description:
        - The tenant name of the login user
     required: true
     default: 'yes'
   auth_url:
     description:
        - The keystone url for authentication
     required: false
     default: 'http://127.0.0.1:35357/v2.0/'
   region_name:
     description:
        - Name of the region
     required: false
     default: None
   flavorid:
     description:
        - Unique flavor ID
     required: false
     default: 'auto'
   name:
     description:
        - New flavor name
     required: true
     default: None
   ram:
     description:
        - Memory size in MB
     required: true
     default: None
   disk:
     description:
        - Disk size in GB
     required: true
     default: None
   ephemeral:
     description:
        - Ephemeral disk size in GB
     required: false
     default: None
   swap:
     description:
        - Swap space size in GB
     required: false
     default: None
   vcpus:
     description:
        - Number of vcpus
     required: true
     default: None
   rxtx-factor:
     description:
        - RX/TX factor
     required: false
     default: None
   is_public:
     description:
        - Indicate if flavor is available to other projects
     required: false
     default: True

requirements: ["novaclient"]
author: Guang Yee
'''
EXAMPLES = '''
# Creates a new flavor
- create_flavor: login_username=admin login_password=admin
            login_tenant_name=admin name=m1.tiny id=1 ram=512 vcpus=1

'''


def _find_flavor(client, name):
    """ Return the first flavor which matches the given name """
    for flavor in client.flavors.list():
        if flavor.name == name:
            return flavor


def create_flavor(client, name, ram, vcpus, disk, **args):
    """ Create a new flavor if one does not exist. """
    flavor = _find_flavor(client, name)
    if flavor:
        return dict(changed=False, id=flavor.id)

    flavor = client.flavors.create(name, ram, vcpus, disk, **args)
    return dict(changed=True, id=flavor.id)


def main():
    module = AnsibleModule(  # noqa
        argument_spec=dict(
            auth_url=dict(required=False,
                          default='http://127.0.0.1:35357/v3'),
            login_project_name=dict(required=False, default='service'),
            login_project_domain_name=dict(required=False, default='Default'),
            login_username=dict(required=False, default='nova'),
            login_user_domain_name=dict(required=False, default='Default'),
            login_password=dict(required=False, default='password'),
            region_name=dict(required=False, default='RegionOne'),
            name=dict(required=True),
            ram=dict(required=True),
            vcpus=dict(required=True),
            disk=dict(required=True),
            flavorid=dict(required=False),
            ephemeral=dict(required=False),
            swap=dict(required=False),
            rxtx_factor=dict(required=False),
            is_public=dict(required=False)
        ),
        supports_check_mode=False
    )

    optional_args = {}
    for arg in ['flavorid', 'ephemeral', 'swap', 'rxtx_factor', 'is_public']:
        if arg in module.params and module.params[arg] is not None:
            optional_args[arg] = module.params[arg]

    ks_auth = v3.Password(
        auth_url=module.params['auth_url'],
        username=module.params['login_username'],
        user_domain_name=module.params['login_user_domain_name'],
        project_name=module.params['login_project_name'],
        project_domain_name=module.params['login_project_domain_name'],
        password=module.params['login_password'])
    ks_session = session.Session(auth=ks_auth)

    client = nova_client.Client('2',
                                session=ks_session,
                                region_name=module.params['region_name'],
                                service_type='compute',
                                endpoint_type='internalURL')

    try:
        d = create_flavor(client, module.params['name'], module.params['ram'],
                          module.params['vcpus'], module.params['disk'],
                          **optional_args)
    except Exception, e:
            module.fail_json(msg='Exception: %s' % e)
    else:
        module.exit_json(**d)


if __name__ == "__main__":
    main()
