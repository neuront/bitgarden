import os

import tornado.ioloop
import tornado.httpserver
import tornado.web

import appenv
import handlers

def main():
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    application = tornado.web.Application([
            (r'/', handlers.Index),
            (r'/addtopic', handlers.AddTopic),
            (r'/topic', handlers.SingleTopic),
            (r'/addcomment', handlers.AddComment),
            (r'/search', handlers.Search),
            (r'/static/(.*)', tornado.web.StaticFileHandler,
                dict(path=static_path)),
        ],
    )

    tornado.httpserver.HTTPServer(application).listen(appenv.env().server_port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__': main()
