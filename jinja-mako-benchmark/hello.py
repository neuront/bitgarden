import tornado.httpserver
import tornado.web
import tornado.ioloop
import asyncmongo
import render

db = asyncmongo.Client(pool_id='x', dbname='test', host='localhost', port=27017)

class Index(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        db.posts.find(dict(), callback=self.on_result)

    def on_result(self, result, error):
        if error:
            raise tornado.web.HTTPError(500)
        self.write(render.render('index.html', posts=result))
        self.finish()

def main():
    application = tornado.web.Application([
            (r'/', Index),
        ],
    )
    tornado.httpserver.HTTPServer(application).listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__': main()
