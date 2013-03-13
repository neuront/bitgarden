import datetime

import asyncmongo
import bson.objectid
import bson.dbref

import appenv

db = asyncmongo.Client(pool_id='mongodemo', dbname='mongodemo',
                       host='localhost', port=appenv.env().db_port)

COUNT_PER_PAGE = 16

def ref(collection, obj):
    return bson.dbref.DBRef(collection, str(obj['_id']))

def add_topic(title, tags, content, cb):
    db.topics.insert({
            'title': title,
            'tags': tags,
            'content': content,
            'post_time': datetime.datetime.utcnow(),
        }, callback=cb)

def topic_only(uid, cb):
    db.topics.find_one({'_id': bson.objectid.ObjectId(uid)}, callback=cb)

def query(criterion, cb):
    cri = dict()
    if criterion['title']:
        cri['title'] = criterion['title']
    if len(criterion['tags']) > 0:
        cri['tags'] = { '$all' : criterion['tags'] }
    db.topics.find(cri, callback=cb)

def first_page(cb):
    db.topics.find({}, limit=COUNT_PER_PAGE, callback=cb)

def add_comment(tid, content, cb):
    db.comments.insert({
            'topic': bson.dbref.DBRef('topics', tid),
            'content': content,
            'post_time': datetime.datetime.utcnow(),
        }, callback=cb)

def topic_with_comments(tid, cb):
    def load_comments(topic, error):
        def return_topic(comments, error):
            if error:
                return cb(None, error)
            topic['comments'] = comments
            cb(topic, None)
        if error:
            return cb(None, error)
        db.comments.find({ 'topic': ref('topics', topic) },
                         callback=return_topic)
    topic_only(tid, load_comments)
