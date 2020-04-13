import tornado.ioloop
import tornado.web
from tornado import gen
import time

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        await gen.sleep(1)
        self.write("Hello, world")

class Main2Handler(tornado.web.RequestHandler):
    async def get(self):

        await gen.sleep(2)
        self.write("Hello, world2")

def make_app():
    return tornado.web.Application([
        (r"/1", MainHandler),
        (r"/2", Main2Handler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
