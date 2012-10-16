import logging
import threading

from kombu import Connection, Exchange, Queue


class ConsumerThread(threading.Thread):

    def __init__(self, broker_url, exchange, exchange_type, queue,
                       routing_key, durable=True):
        threading.Thread.__init__(self)
        self.daemon = True

        self._callbacks = []
        self._broker_url = broker_url

        self._exchange = Exchange(exchange, exchange_type, durable=durable)
        self._queue = Queue(queue, exchange=self._exchange, routing_key=routing_key)

    def start(self):
        threading.Thread.start(self)

    def add_callback(self, callback):
        assert not self.is_alive()
        self._callbacks.append(callback)

    def run(self):
        with Connection(self._broker_url) as conn:
            with conn.Consumer(self._queue, callbacks=self._callbacks):
                logging.info('Connected to: %s' % conn.as_uri())
                while True:
                    conn.drain_events()
