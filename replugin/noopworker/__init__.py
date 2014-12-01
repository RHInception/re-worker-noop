# -*- coding: utf-8 -*-
# Copyright © 2014 SEE AUTHORS FILE
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
Noop worker.
"""

import xmlrpclib

from reworker.worker import Worker


class NoopWorkerError(Exception):
    """
    Base exception class for NoopWorker errors.
    """
    pass


class NoopWorker(Worker):
    """
    A simple noop worker who just echos back input parameters.

Use the special 'fail' subcommand to force a failure in a step
    """

    def verify_subcommand(self, parameters):
        """Verify we were supplied with a valid subcommand

NOOP worker is special. It accepts all subcommands and outputs/notifys
all input (dynamic/parameters)
        """
        return True

    def process(self, channel, basic_deliver, properties, body, output):
        """Processes requests from the bus.
        """
        # Ack the original message
        self.ack(basic_deliver)
        corr_id = str(properties.correlation_id)

        self.app_logger.info("Starting now")
        # Tell the FSM that we're starting now
        self.send(
            properties.reply_to,
            corr_id,
            {'status': 'started'},
            exchange=''
        )

        self.notify(
            "Subject",
            "Message",
            'started',
            corr_id
        )
        output.info("Starting now")

        try:
            self.verify_subcommand(body['parameters'])

            subcmd = body['parameters'].get('subcommand', 'noop')
            # update the parameters dict w/ what we discovered (it may
            # not have been set before, no no!)
            body['parameters']['subcommand'] = subcmd

            if subcmd != 'Fail':
                self.app_logger.info("Did the needful")
                self.send(
                    properties.reply_to,
                    corr_id,
                    {'status': 'completed'},
                    exchange=''
                )
                # Notify over various other comm channels about the result
                self.notify(
                    'Noopworker success',
                    str(body),
                    'completed',
                    corr_id)

                # Output to the general logger (taboot tailer perhaps)
                output.info('NOOP worker succeeded - %s' % str(body))
                return True
            else:
                raise NoopWorkerError("noop error - %s" % str(body))

        except NoopWorkerError, e:
            # If an error happens send a failure and log it to stdout
            self.app_logger.error('Failure: %s' % e)
            # Send a message to the FSM indicating a failure event took place
            self.send(
                properties.reply_to,
                corr_id,
                {'status': 'failed'},
                exchange=''
            )
            # Notify over various other comm channels about the event
            self.notify(
                'Noop Worker Failed',
                str(e),
                'failed',
                corr_id)
            # Output to the general logger (taboot tailer perhaps)
            output.error(str(e))


def main():  # pragma: no cover
    from reworker.worker import runner
    runner(NoopWorker)


if __name__ == '__main__':  # pragma nocover
    main()
