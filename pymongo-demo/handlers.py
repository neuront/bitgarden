import json

import jinja2
import tornado.web

import models

templ_env = jinja2.Environment(loader=jinja2.FileSystemLoader('./templates'))

def render(filename, **kwargs):
    return templ_env.get_template(filename).render(**kwargs)

class BaseHandler(tornado.web.RequestHandler):
    def arg(self, key):
        return self.args(key)[0] if key in self.request.arguments else None

    def args(self, key):
        return self.request.arguments[key]

    def write_json(self, obj):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(obj))

class AsyncHandler:
    @tornado.web.asynchronous
    def serve(self):
        def callback(result, error):
            if error:
                raise tornado.web.HTTPError(500)
            if self.on_result(result) is None:
                self.finish()
        self.async_call(callback, **self.query_args())

class AsyncGetHandler(BaseHandler, AsyncHandler):
    @tornado.web.asynchronous
    def get(self):
        self.serve()

class AsyncPostHandler(BaseHandler, AsyncHandler):
    @tornado.web.asynchronous
    def post(self):
        self.serve()

class Index(AsyncGetHandler):
    def initialize(self):
        self.async_call = models.first_page

    def query_args(self):
        return dict()

    def on_result(self, result):
        self.write(render('index.html', topics=result))

class SingleTopic(AsyncGetHandler):
    def initialize(self):
        self.async_call = models.topic_with_comments

    def query_args(self):
        return { 'topic_id': self.arg('id') }

    def on_result(self, result):
        if result:
            self.write(render('topic.html', topic=result))
        else:
            self.set_status(404)
            self.write(render('not-found.html'))

class Search(AsyncGetHandler):
    def initialize(self):
        self.async_call = models.query

    def query_args(self):
        tags = self.arg('tags')
        if not tags:
            tags = ''
        self.tags = filter(lambda s: len(s) > 0, tags.split(','))
        return { 'title': self.arg('title'), 'tags': self.tags }

    def on_result(self, result):
        self.write(render('search-result.html', topics=result, tags=self.tags))

class AddTopic(AsyncPostHandler):
    def initialize(self):
        self.async_call = models.add_topic

    def query_args(self):
        return {
                'title': self.arg('title'),
                'tags': [ t.strip() for t in self.arg('tags').split(',') ],
                'content': self.arg('content'),
            }

    def on_result(self, result):
        self.redirect('/')
        return True

class AddComment(AsyncPostHandler):
    def initialize(self):
        self.async_call = models.add_comment

    def query_args(self):
        self.topic_id = self.arg('topic_id')
        return {
                'topic_id': self.topic_id,
                'content': self.arg('content'),
            }

    def on_result(self, result):
        self.redirect('/topic?id=' + self.topic_id)
        return True
