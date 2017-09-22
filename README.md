<!--

 (c) Copyright 2015-2017 Hewlett Packard Enterprise Development LP
 (c) Copyright 2017 SUSE LLC

 Licensed under the Apache License, Version 2.0 (the "License"); you may
 not use this file except in compliance with the License. You may obtain
 a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 License for the specific language governing permissions and limitations
 under the License.

-->
NOVA-ANSIBLE
============

This repo contains the following roles and role specific tasks:
- NOV-API - API service.
- NOV-CLI - Contains tasks that use the nova client.
  - availability_zones - Configure availability zones - used by nova-cloud-configure.
- nova-common - Common variables and tasks across services.
  - _configure_policy - Configure policy for service.
  - _configure_rootwrap - Configure rootwrap for service.
  - _service_status - Check and report status of service.
  - _set_directories - Set directories (etc, bin, conf) for service.
  - _singleton_service_status - Check and report status of a singleton service.
  - _write_conf - Create a file, maintaining backup copies.
- NOV-CMP - Compute service which requires one of the hypervisors.
- NOV-CMP-ESX - ESX hypervisor.
- NOV-CMP-IRN - Ironic hypervisor.
- NOV-CMP-KVM - KVM hypervisor.
- NOV-CND - Conductor service.
- NOV-CAU - Consoleauth service.
- nova-monasca - Monitoring
  - heartbeat_alarm - Install and configure a heartbeat check.
  - _monitor_libvirt - Run Monasca agent libvirt detection plugin.
  - process_bounds_alarm - Run a check on the number of nova-api processes.
  - start - Run Monasca agent Nova detection plugin.
- nova-post-configure - Configuration operations that are run after all
 services are configured.
  - db_configure - Configure the nova database.
  - db_contract - Remove rows/columns etc. from the nova database during
 upgrade.
  - db_create - Create the nova database.
  - db_expand - Add rows/columns etc. to the nova database during upgrade.
  - keystone_conf - Configure the Keystone service for nova.
  - rabbit_configure - Configure the RabbitMQ service for nova.
  - create_defalut_flavors - Add the default flavors if they don't exist.
- NOV-SCH - Scheduler service
- NOV-SCH-IRN - Ironic specific configuration for nova scheduler service.
- NOV-VNC - VNC service

Within each service role the following tasks may exist:
- check_upgraded_packages - Notify the restart handler when a service needs
 to be restarted due to a package being updated.
- configure               - Configure the service.
- install                 - Install the service.
- start                   - Start the service.
- status                  - Report status of the service.
- stop                    - Stop the service.

Top level playbooks:

  - _nova-check-upgraded-packages - Check upgraded packages for all nova services - used by upgrade.
  - nova-cloud-configure          - Cloud configuration - optionally run manually by users.
  - nova-configure                - Configure all nova components - used by deploy & reconfigure.
  - nova-deploy                   - Deploy the service (install, configure and start).
  - _nova-install                 - Install all nova components - used by deploy & upgrade.
  - _nova-post-configure          - Post configuration operations - used by deploy & reconfigure.
  - _nova-post-deploy             - Post deploy operations - used by deploy & reconfigure.
  - nova-reconfigure              - Reconfigure all nova components.
  - nova-start                    - Start all nova services.
  - nova-status                   - Status of all nova services.
  - nova-stop                     - Stop all nova services.
  - nova-upgrade                  - Upgrade all nova components.
