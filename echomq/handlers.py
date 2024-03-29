import logging

import tornadio2
import tornadio2.router
import tornadio2.server


class ClientConnection(tornadio2.SocketConnection):
    clients = set()

    def on_open(self, *args, **kwargs):
        self.clients.add(self)
        self.send('Welcome!')
        logging.debug('Connected')

    def on_message(self, message):
        pass

    def on_close(self):
        self.clients.remove(self)
        logging.debug('Disconnected')

    @classmethod
    def broadcast(cls, body, message):
        for c in cls.clients:
            try:
                c.send(body)
            except Exception as e:
                logging.exception(e)

    @classmethod
    def get_router(cls):
        return tornadio2.TornadioRouter(cls)
