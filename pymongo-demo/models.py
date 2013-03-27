import datetime

import asyncmongo
import bson.objectid
import bson.dbref

import appenv

def asynchronous(callback):
    def wrapper(f):
        def g(result, error):
            if error:
                return callback(None, error)
            f(result)
        return g
    return wrapper

def ensynchronous(callback):
    def wrapper(f):
        def g(result, error):
            if error:
                return callback(None, error)
            return callback(f(result), None)
        return g
    return wrapper

db = asyncmongo.Client(pool_id='mongodemo', dbname='mongodemo',
                       host='localhost', port=appenv.env().db_port)

COUNT_PER_PAGE = 16

def ref(collection, obj):
    return bson.dbref.DBRef(collection, str(obj['_id']))

def add_topic(cb, title, tags, content):
    db.topics.insert({
            'title': title,
            'tags': tags,
            'content': content,
            'post_time': datetime.datetime.utcnow(),
        }, callback=cb)

def topic_only(uid, cb):
    db.topics.find_one({'_id': bson.objectid.ObjectId(uid)}, callback=cb)

def query(cb, title, tags):
    cri = dict()
    if title: cri['title'] = title
    if len(tags) > 0: cri['tags'] = { '$all' : tags }
    db.topics.find(cri, callback=cb)

def first_page(cb):
    db.topics.find({}, limit=COUNT_PER_PAGE, callback=cb)

def add_comment(cb, topic_id, content):
    db.comments.insert({
            'topic': bson.dbref.DBRef('topics', topic_id),
            'content': content,
            'post_time': datetime.datetime.utcnow(),
        }, callback=cb)

def topic_with_comments(cb, topic_id):
    @asynchronous(cb)
    def load_comments(topic):
        @ensynchronous(cb)
        def return_topic(comments):
            topic['comments'] = comments
            return topic
        db.comments.find({ 'topic': ref('topics', topic) },
                         callback=return_topic)
    topic_only(topic_id, load_comments)
