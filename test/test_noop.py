# Copyright (C) 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Unittests.
"""

import mock

from . import TestCase
from contextlib import nested

from replugin import noopworker

MQ_CONF = {
    'server': '127.0.0.1',
    'port': 5672,
    'vhost': '/',
    'user': 'guest',
    'password': 'guest',
}


class TestNoop(TestCase):
    def setUp(self):
        """
        Set up some reusable mocks.
        """
        TestCase.setUp(self)

        self.channel = mock.MagicMock('pika.spec.Channel')

        self.channel.basic_consume = mock.Mock('basic_consume')
        self.channel.basic_ack = mock.Mock('basic_ack')
        self.channel.basic_publish = mock.Mock('basic_publish')

        self.basic_deliver = mock.MagicMock()
        self.basic_deliver.delivery_tag = 123

        self.properties = mock.MagicMock(
            'pika.spec.BasicProperties',
            correlation_id=123,
            reply_to='me')

        self.logger = mock.MagicMock('logging.Logger').__call__()
        self.app_logger = mock.MagicMock('logging.Logger').__call__()
        self.connection = mock.MagicMock('pika.SelectConnection')

    def tearDown(self):
        """
        After every test.
        """
        TestCase.tearDown(self)
        self.channel.reset_mock()
        self.channel.basic_consume.reset_mock()
        self.channel.basic_ack.reset_mock()
        self.channel.basic_publish.reset_mock()

        self.basic_deliver.reset_mock()
        self.properties.reset_mock()

        self.logger.reset_mock()
        self.app_logger.reset_mock()
        self.connection.reset_mock()

    def test_noop_worker_pass(self):
        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.noopworker.NoopWorker.notify'),
                mock.patch('replugin.noopworker.NoopWorker.send')):

            worker = noopworker.NoopWorker(
                MQ_CONF,
                logger=self.app_logger,
                config_file='conf/example.json')

            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            self.assertTrue(worker.verify_subcommand({}))

            body = {
                "parameters": {
                    "command": "noop",
                    "subcommand": "EveryBodyWinsAPony",
                }
            }

            result = worker.process(
                self.channel,
                self.basic_deliver,
                self.properties,
                body,
                self.logger)

    def test_noop_worker_fail(self):
        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.noopworker.NoopWorker.notify'),
                mock.patch('replugin.noopworker.NoopWorker.send')):

            worker = noopworker.NoopWorker(
                MQ_CONF,
                logger=self.app_logger,
                config_file='conf/example.json')

            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            body = {
                "parameters": {
                    "command": "noop",
                    "subcommand": "Fail",
                }
            }

            result = worker.process(
                self.channel,
                self.basic_deliver,
                self.properties,
                body,
                self.logger)

            self.assertEqual(self.app_logger.error.call_count, 1)
            self.assertEqual(worker.send.call_args[0][2]['status'], 'failed')
