#!/usr/bin/env python

import config
import os.path
import tornado.ioloop
import tornado.web



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", title="My title")

    def post(self):
        self.set_header("Content-Type", "text/plain")
        self.write("You wrote " + self.get_body_argument("message"))



class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]

        settings = {
            "debug": True,
            "template_path": os.path.join("templates"),
            "static_path": os.path.join("static")
        }

        tornado.web.Application.__init__(self, handlers, **settings)



if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()