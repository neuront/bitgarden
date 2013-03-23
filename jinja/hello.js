var jinjs = require('jinjs');
jinjs.registerExtension('.html');
var index = require('./templates/index');

function Tester(test_content) {
    this.echo_0 = function() {
        return test_content;
    };
    this.echo_1 = function(additional_content) {
        return test_content + additional_content;
    };
}

console.log(index.render({ t: new Tester('Hello') }));
