import socket
import logging
import threading

from tornado import ioloop
from kombu import Connection, Exchange, Queue


class ConsumerThread(threading.Thread):

    def __init__(self, broker_url, exchange, exchange_type, queue,
                       routing_key, durable=True, ssl=False):
        threading.Thread.__init__(self)
        self.daemon = True
        self._running = False

        self._callbacks = []
        self._broker_url = broker_url
        self._ssl = ssl

        self._exchange = Exchange(exchange, exchange_type, durable=durable)
        self._queue = Queue(queue, exchange=self._exchange, routing_key=routing_key)

    def start(self):
        threading.Thread.start(self)

    def stop(self):
        self._running = False

    def add_callback(self, callback):
        assert not self.is_alive()
        self._callbacks.append(callback)

    def run(self):
        try:
            with Connection(self._broker_url, ssl=self._ssl) as conn:
                with conn.Consumer(self._queue, callbacks=self._callbacks):
                    logging.info('Connected to: %s' % conn.as_uri())
                    self._running = True
                    while self._running:
                        try:
                            conn.drain_events(timeout=5)
                        except socket.timeout:
                            pass
        except (KeyboardInterrupt, SystemExit):
            import thread
            thread.interrupt_main()


class TornadoConsumer(object):
    """Non-blocking, Tornado ioloop based consumer"""

    def __init__(self, broker_url, exchange, exchange_type, queue,
                       routing_key, durable=True, ssl=False, io_loop=None):
        self.io_loop = io_loop or ioloop.IoLoop.instance()
        self._conn = None
        self._callbacks = []
        self._broker_url = broker_url
        self._ssl = ssl

        self._exchange = Exchange(exchange, exchange_type, durable=durable)
        self._queue = Queue(queue, exchange=self._exchange, routing_key=routing_key)

    def add_callback(self, callback):
        assert not self._conn
        self._callbacks.append(callback)

    def start(self):
        self._conn = Connection(self._broker_url, self._ssl)
        self._consumer = self._conn.Consumer(self._queue, callbacks=self._callbacks)
        self.io_loop.add_handler(self._conn.fileno(), self._handle_event)

    def stop(self):
        self.io_loop.remove_handler(self._conn.fileno())
        self._consumer.close()
        self._conn.release()

    def join(self, *args, **kwargs):
        pass

    def _handle_event(self):
        self._conn.drain_nowait()
