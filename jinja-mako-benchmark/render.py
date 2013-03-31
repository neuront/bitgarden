import sys
import os
import jinja2
import tempfile
import mako.lookup

jinja = jinja2.Environment(loader=jinja2.FileSystemLoader('./jinja'))
mako_lookup = mako.lookup.TemplateLookup(
                    os.path.join(os.getcwd(), 'mako'),
	                os.path.join(tempfile.gettempdir(), 'mako_cache'),
                    output_encoding='utf=8', input_encoding='utf-8')

def jrender(filename, **kwargs):
    return jinja.get_template(filename).render(**kwargs)

def mrender(filename, **kwargs):
    return mako_lookup.get_template(filename).render(**kwargs)

if len(sys.argv) > 1 and sys.argv[1] == 'mako':
    print 'Use mako'
    render = mrender
else:
    print 'Default use jinja2'
    render = jrender
