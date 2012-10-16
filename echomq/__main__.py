import logging
import argparse

from functools import partial

import tornadio

from consumer import ConsumerThread
from handlers import ClientConnection
from app import Application


def main():
    parser = argparse.ArgumentParser(description='Message dispatcher')
    parser.add_argument('--broker-url', type=str, required=True,
                        help='Broker to consume from')
    parser.add_argument('--exchange', type=str, required=True,
                        help='Exchange name')
    parser.add_argument('--exchange-type', type=str, default='direct',
                        help='Exchange type (default direct)')
    parser.add_argument('--routing-key', required=True, type=str,
                        help='Routing key')
    parser.add_argument('--queue', type=str, required=True,
                        help='Queue name')
    parser.add_argument('--debug', type=bool, default=False,
                        help='Enable debugging')
    parser.add_argument('--socket-io-port', type=int, default=8001,
                        help='Socket.IO port number')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    handlers = [ClientConnection.get_router().route()]
    app = Application(handlers, socket_io_port=args.socket_io_port)
    def process_message(body, message):
        app.io_loop.add_callback(partial(ClientConnection.broadcast,
                                         body, message))
        message.ack()
    consumer = ConsumerThread(broker_url=args.broker_url,
                              exchange=args.exchange,
                              exchange_type=args.exchange_type,
                              queue=args.queue,
                              routing_key=args.routing_key)
    consumer.add_callback(process_message)
    consumer.start()

    tornadio.server.SocketServer(app)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    main()
