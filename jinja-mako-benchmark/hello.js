var jinjs = require('jinjs');
jinjs.registerExtension('.html');
var index = require('./jinja/index');
var db = require('mongojs')('test');

require("http").createServer(function(request, response) {
    db.collection('posts').find(function(err, posts) {
        if (err) {
            response.writeHead(500);
        } else {
            response.writeHead(200, {'Content-Type': 'text/html'});
            response.write(index.render({ posts: posts }));
        }
        response.end();
    });
}).listen(8888);
