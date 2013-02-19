# -*- coding: utf-8 -*-

import time
import http.server as httpserver

import itertools as it
from functools import partial, reduce
import operator as op

import pymongo #install latest ``distribute'' to install pip-3.2 to install pymongo for

HOSTNAME = 'localhost'
PORT = 80

def unpack(f, a):
    return f(*a)
def unpackd(f,a):
    return f(**a)

def tee(a):
    print(a)
    return a

padding = partial(op.add, " "*4)

def tag(name, *content, **attributes):
    return "<{name}{attributes}>\n{content}\n</{name}>".format(
        name=name,
        content='\n'.join(content),
        attributes=reduce(op.add,
            map(
                partial(
                    unpack,
                    ' {0}="{1}"'.format
                ),
                attributes.items()
            ),
            ""
        )
    )

class Path(object):
    def __init__(self, m):
        self.directory, *variablestring = m.split('?')
        self.folders = list(filter(bool, self.directory.split('/')))
        if(variablestring):
            def parse_variable(v):
                return tuple(v.split("="))
            self.variables = dict(
                map(
                    parse_variable,
                    variablestring[0].split("&")
                )
            )
        else:
            self.variables = []

    def __repr__(self):
        return "Path(folders={folders}, variables={variables})".format(folders=self.folders, variables=self.variables)
 
class Handler(httpserver.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/xml")
        s.end_headers()

    def do_GET(s):
        """Responde to a GET request"""

        def write(m, encoding="utf-8"):
            s.wfile.write(
                bytes(
                    m, 
                    encoding=encoding
                )
            )
        
        def render_item(item):
            def CDATA(data):
                return "<![CDATA[{data}]]>".format(data=data)
            return tag("item",
                *map(
                    lambda name: tag(
                        name, 
                        padding(
                            CDATA(
                                item[name]
                            )
                        )
                    ),
                    it.filterfalse(
                        op.methodcaller('startswith', '_'),
                        item
                    )
                )
            )

        path = Path(s.path)
        print(path)
        if(len(path.folders)>0 and path.folders[0]=='favicon.ico' or not len(path.folders)):
            s.send_response(404)
            s.end_headers()
            return

        rss_id = path.folders[0]
        
        s.send_response(200)
        s.send_header("Content-type", "text/xml")
        s.end_headers()
        
        database = pymongo.MongoClient('localhost', 1337)['rss-database']
        collection = database[rss_id]

        write('<?xml version="1.0" encoding="UTF-8"?>\n')
        write(
            tag("rss",
                tag("channel",
                    tag("title", "{rss_id} RSS".format(rss_id=rss_id)),
                    tag("link", "{domain}/{rss_id}".format(domain=HOSTNAME, rss_id=rss_id)),
                    tag("description", "RSS feed for {rss_id}".format(rss_id=rss_id)),
                    tag("language", "en-us"),
                    tag("copyright", "Copyright 2013, Jim Holmström"),
                    tag("managingEditor", "me@jim.pm (Jim Holmström)"),
                    tag("webMaster", "me@jim.pm (Jim Holmström)"),
                    *map(                
                        render_item,
                        collection.find().sort('_id') #title/link/description/..
                    )
                ),
            version="2.0"
            )
        )
#db=pymongo.MongoClient('localhost', 1337)['rss-database']
#c=db['SE1055'] 
#a=['1.1','1.2',..]
#d=list(map(lambda t: {'title':t},a))
#c.insert(d)
 
if __name__ == "__main__":
    httpd = httpserver.HTTPServer((HOSTNAME, PORT), Handler)
    print(time.asctime(), "Server start - {name}:{port}".format(name=HOSTNAME, port=PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Server stops - {name}:{port}".format(name=HOSTNAME, port=PORT))

