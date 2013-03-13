function parseArgs() {
  var result = {};
  var url = window.location.href;
  var begin = url.indexOf('?') + 1;
  var end = url.indexOf('#');
  if (end == -1) end = url.length;
  var args = url.slice(begin, end).split('&');
  for(var i = 0;  i < args.length; i++) {
    var p = args[i].split('=');
    result[p[0]] = decodeURIComponent(p[1]);
  }
  return result;
}

function makeArgs(args) {
  var result = [];
  for (var key in args) {
    result.push(encodeURIComponent(key) + '=' + encodeURIComponent(args[key]));
  }
  return '?' + result.join('&');
}
