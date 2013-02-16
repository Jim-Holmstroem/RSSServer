# -*- coding: utf-8 -*-


import time
import http.server as httpserver

from functools import partial, reduce
import operator as op

import pymongo

HOSTNAME = 'localhost'
PORT = 80

def unpack(f, a):
    return f(*a)
def unpackd(f,a):
    return f(**a)

def printer(a):
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

class Handler(httpserver.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/xml")
        s.end_headers()

    def do_GET(s):
        """Responde to a GET request"""
        s.send_response(200)
        s.send_header("Content-type", "text/xml")
        s.end_headers()

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
                    lambda name: 
                    tag(name, padding(CDATA(item[name]))),
                    item
                )
            )

        rss_id = "SE1055"
        domain = "http://jimboslice.no-ip.com"

        write('<?xml version="1.0" encoding="UTF-8"?>\n')
        write(
            tag("rss",
                tag("channel",
                    tag("title", "{rss_id} RSS".format(rss_id=rss_id)),
                    tag("link", "{domain}/{rss_id}".format(domain=domain, rss_id=rss_id)),
                    tag("description", "RSS feed for {rss_id}".format(rss_id=rss_id)),
                    tag("language", "en-us"),
                    tag("copyright", "Copyright 2013, Jim Holmström"),
                    tag("managingEditor", "me@jim.pm (Jim Holmström)"),
                    tag("webMaster", "me@jim.pm (Jim Holmström)"),
                    *map(                
                        render_item,
                        [
                            dict(title='1.11',link='http://link.com',description='desc',comments='comment'),
                            dict(title='1.11',link='http://link.com',description='desc',comments='comment'),
                        ]
                    )
                ),
            version="2.0"
            )
        )
        

if __name__ == "__main__":
    httpd = httpserver.HTTPServer((HOSTNAME, PORT), Handler)
    print(time.asctime(), "Server start - {name}:{port}".format(name=HOSTNAME, port=PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Server stops - {name}:{port}".format(name=HOSTNAME, port=PORT))
