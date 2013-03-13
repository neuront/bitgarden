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

class Index(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        models.first_page(self.on_result)

    def on_result(self, result, error):
        if error:
            raise tornado.web.HTTPError(500)
        self.write(render('index.html', topics=result))
        self.finish()

class SingleTopic(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        models.topic_with_comments(self.arg('id'), self.on_result)

    def on_result(self, result, error):
        if error:
            raise tornado.web.HTTPError(500)
        if result:
            self.write(render('topic.html', topic=result))
        else:
            self.set_status(404)
            self.write(render('not-found.html'))
        self.finish()

class Search(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        tags = self.arg('tags')
        if not tags:
            tags = ''
        self.tags = filter(lambda s: len(s) > 0, tags.split(','))
        models.query({ 'title': self.arg('title'), 'tags': self.tags },
                     self.on_result)

    def on_result(self, result, error):
        if error:
            raise tornado.web.HTTPError(500)
        self.write(render('search-result.html', topics=result, tags=self.tags))
        self.finish()

class AddTopic(BaseHandler):
    @tornado.web.asynchronous
    def post(self):
        models.add_topic(self.arg('title'),
                         [ t.strip() for t in self.arg('tags').split(',') ],
                         self.arg('content'), self.on_result)

    def on_result(self, result, error):
        if error:
            raise tornado.web.HTTPError(500)
        self.redirect('/')

class AddComment(BaseHandler):
    @tornado.web.asynchronous
    def post(self):
        self.topic_id = self.arg('topic_id')
        models.add_comment(self.topic_id, self.arg('content'), self.on_result)

    def on_result(self, result, error):
        if error:
            raise tornado.web.HTTPError(500)
        self.redirect('/topic?id=' + self.topic_id)
