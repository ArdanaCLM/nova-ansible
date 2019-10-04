#
# (c) Copyright 2015 Hewlett Packard Enterprise Development LP
# (c) Copyright 2017 SUSE LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

import json
def pci_passthrough_filter_whitelist(collection):
     '''
     returning the alias list
     '''

     plist = []
     for x in collection:
        if ("bus_address" in x) and (len(x["bus_address"]) > 0):
           plist.append(dict(address=x['bus_address']))
        else:
           plist.append(dict(
            vendor_id=x['vendor_id'],
            product_id=x['product_id']))

     return plist

def pci_passthrough_filter_alias(collection):
     '''
     returning the gpu pci whitelist list
     '''

     pcilist = []

     for x in collection:
        pcilist.append(dict(
          vendor_id=x['vendor_id'],
          product_id=x['product_id'],
          device_type=x['pf_mode'],
          name=x['name']))

     return pcilist

class FilterModule(object):
    '''
    custom jinja2 filters for working with collections
    '''

    def filters(self):
        return {
            'pci_passthrough_filter_whitelist': pci_passthrough_filter_whitelist,
            'pci_passthrough_filter_alias': pci_passthrough_filter_alias
        }
