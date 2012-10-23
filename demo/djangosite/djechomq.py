# Sample application demonstrating echomq usage with django
#
# Run with PYTHONPATH=..:../.. DJANGO_SETTINGS_MODULE=djangosite.settings python djechomq.py --broker-url=amqp://localhost --port=8001 --queue=test
#

import os
import logging
import argparse

from functools import partial

import tornado
import tornado.wsgi
import tornadio
import django.core.handlers.wsgi

from echomq.consumer import ConsumerThread
from echomq.handlers import ClientConnection
from echomq.app import Application


class HelloHandler(tornado.web.RequestHandler):
  def get(self):
    self.write('Hello from tornado!')


def main():
    assert os.environ['DJANGO_SETTINGS_MODULE']
    logging.getLogger().setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description='Generic echo server')
    parser.add_argument('--broker-url', type=str, required=True,
                        help='Broker to consume from')
    parser.add_argument('--queue', type=str, required=True,
                        help='Queue name')
    parser.add_argument('--port', type=int, default=8001,
                        help='Web server port number')

    logging.debug('Parsing the command line arguments...')
    args = parser.parse_args()

    wsgi_app = tornado.wsgi.WSGIContainer(
                    django.core.handlers.wsgi.WSGIHandler())

    handlers = [ClientConnection.get_router().route()]
    handlers.extend([
        ('/hello-tornado', HelloHandler),
        ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
    ])

    app = Application(handlers, socket_io_port=args.port)
    def process_message(body, message):
        app.io_loop.add_callback(partial(ClientConnection.broadcast,
                                         body, message))
        message.ack()
    logging.debug('Starting a consumer thread...')
    consumer = ConsumerThread(broker_url=args.broker_url,
                              exchange='test',
                              exchange_type='direct',
                              queue=args.queue,
                              routing_key='')
    consumer.add_callback(process_message)
    consumer.start()

    logging.debug('Starting a socket server...')
    tornadio.server.SocketServer(app)


if __name__ == "__main__":
    main()
