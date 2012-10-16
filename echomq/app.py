from tornado import web
from tornado import ioloop


class Application(web.Application):
    def __init__(self, handlers, io_loop=None, **kwargs):
        kwargs.update(handlers=handlers)
        super(Application, self).__init__(**kwargs)
        self.io_loop = io_loop or ioloop.IOLoop.instance()

    def start(self, port, address=''):
        self.listen(port, address=address)
        self.io_loop.start()
