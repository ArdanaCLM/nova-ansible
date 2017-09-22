#
# (c) Copyright 2015-2016 Hewlett Packard Enterprise Development LP
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

import mock
import unittest

import keystoneclient
import NOV_MON.nova_heartbeat_check as nhc
from novaclient import client as novacli


class TestNovaHeartbeatCheck(unittest.TestCase):
    def setUp(self):
        nhc.THIS_HOST = 'this_host'
        # Create without calling __init__, as that takes several parameters
        self.nhc = nhc.NovaHeartbeatCheck.__new__(nhc.NovaHeartbeatCheck)
        self.nhc.client = None
        self.nhc.log = mock.MagicMock()

    def test_metric1(self):
        metric = nhc.metric()
        self.assertNotIn('value_meta', metric)
        self.assertEqual('nova.heartbeat', metric['metric'])
        self.assertEqual(nhc.FAIL, metric['value'])
        dims = metric['dimensions']
        self.assertEqual('compute', dims['service'])
        self.assertIsNotNone(dims['observer_hostname'])

    def test_metric2(self):
        metric = nhc.metric(message='omg', cat='meow')
        self.assertEqual('omg', metric['value_meta']['msg'])
        dims = metric['dimensions']
        self.assertEqual('meow', dims['cat'])

    @mock.patch.object(novacli.Client, '__init__',
                       return_value=None)
    @mock.patch.object(keystoneclient.session.Session, '__init__',
                       return_value=None)
    @mock.patch.object(keystoneclient.auth.identity.v3.Password, '__init__',
                       return_value=None)
    def test_get_client(self, mock_pass, mock_session, mock_client):
        self.nhc.init_config = {'keystone': {'project_name': 'aa'},
                                'nova': {'endpoint_type': 'bb'}}
        client = self.nhc._get_client()
        self.assertIsNotNone(client)

    def mk_service(self, **kwargs):
        data = {'status': 'enabled',
                'binary': 'nova-compute',
                'zone': 'nova',
                'state': 'up',
                'updated_at': '2015-10-03T02:33:38.000000',
                'host': 'this_host',
                'disabled_reason': None,
                'id': 31}
        data.update(kwargs)
        svc = mock.MagicMock()
        for k, v in data.items():
            setattr(svc, k, v)
        return svc

    def test_get_state(self):
        svc = self.mk_service()
        self.assertEqual('enabled', svc.status)
        self.assertEqual('nova-compute', svc.binary)
        self.assertEqual(nhc.OK, self.nhc._get_state(svc))

        svc.state = 'down'
        self.assertEqual(nhc.FAIL, self.nhc._get_state(svc))

        svc.status = 'disabled'
        self.assertEqual(nhc.OK, self.nhc._get_state(svc))

        svc.state = 'up'
        self.assertEqual(nhc.OK, self.nhc._get_state(svc))

    def test_gather_metrics(self):
        @mock.patch.object(self.nhc, '_get_client')
        def fn(mock_client):
            mock_client.return_value.services.list.return_value = [
                self.mk_service(),
                self.mk_service(host='other_host'),
            ]
            return self.nhc._gather_metrics()

        metrics = fn()
        self.assertEqual(2, len(metrics))
        self.assertEqual('this_host', metrics[0]['dimensions']['hostname'])
        self.assertEqual('other_host', metrics[1]['dimensions']['hostname'])

    def test_check(self):
        metrics = [nhc.metric(state=nhc.OK, hostname='this_host'),
                   nhc.metric(state=nhc.FAIL, hostname='this_host')]
        instance = mock.sentinel.instance

        @mock.patch.object(self.nhc, 'gauge')
        @mock.patch.object(self.nhc, '_set_dimensions',
                           side_effect=lambda *a: a[0])
        @mock.patch.object(self.nhc, '_gather_metrics',
                           return_value=metrics)
        def fn(mock_gather, mock_dims, mock_gauge):
            self.nhc.check(instance)
            mock_gather.assert_called_once_with()
            self.assertEqual([mock.call(m['dimensions'], instance)
                              for m in metrics],
                             mock_dims.call_args_list)
            self.assertEqual([mock.call(**m) for m in metrics],
                             mock_gauge.call_args_list)
        fn()
