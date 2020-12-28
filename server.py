#!/usr/bin/env python
"""
TODO: doc
"""
import os
import json
import argparse
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from datetime import datetime
from typing import List

parser = argparse.ArgumentParser(description='A simple server to receive and save JSON data')
parser.add_argument('FILE', type=str, help='File to save received data')
parser.add_argument('UPLOAD_DIR', type=str, help='Directory to save uploaded files')
parser.add_argument('-p', '--port', type=int, dest='PORT', default=8888, help='Port for server')
parser.add_argument('-k', '--key', type=str, dest='KEY', default=None, help='Secret key to authenticate clients')
args = parser.parse_args()

""" Sanitize a string for XML """
def s(x): return x.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;').replace('\\t', '   ').replace('\\n', '\n').removesuffix('\n') if x is not None else ""


""" Date format for RSS items """
def to_rss_date(dt): return datetime.fromtimestamp(dt/1000.0).strftime('%a, %d %b %Y %H:%M:%S') + " UTC"
def from_rss_date(text): return datetime.strptime(text, '%a, %d %b %Y %H:%M:%S UTC')

""" Hili clip (python dict) to XML string """
def to_xml(clip):
    tags = clip.get('tags') or []
    return f"""<item>
    <title>{s(clip.get('quote'))}</title>
    <link>{s(clip.get('href'))}</link>
    <description>{s(clip.get('note'))}</description>
    <pubDate>{to_rss_date(clip.get('time'))}</pubDate>
    {"".join([f"<category>{c}</category>" for c in tags]) if len(tags) > 0 else ""}
</item>
"""

""" Load and sanitize XML string from disk """
def str_from_disk() -> str:
    with open(args.FILE, 'r') as f:
        inner = f.read().replace('\\n', '').replace('\\t', '')
    return inner

""" Parse XML on disk and give back a list of clips (python dicts) """
def from_disk() -> List[dict]:
    xml = ET.fromstring(f"<items>{str_from_disk()}</items>")
    clips = []
    for item in xml.iter('item'):
        clips.append({
            'quote': item.find('.title').text,
            'href': item.find('.link').text,
            'note': item.find('.description').text,
            'time': from_rss_date(item.find('.pubDate').text),
            'tags': [t.text for t in item.findall('.category')]
        })
    return clips

def feed_from_disk() -> str: return f"""<rss version="2.0">
<channel>
<title>Hili Clips</title>
<link>https://research.forensic-architecture.org/rss</link>
<description></description>
{str_from_disk()}
</channel>
</rss>
"""

def html_for_attribute(k, val):
    r = ''
    if k == 'quote':
        r = '<i style="color:#666;">'+val+'</i><br/>'
    if k == 'note':
        r = '<span>&nbsp;&nbsp;'+val+'</span><br/>' if val.strip() != '' else ''
    if k == 'tags':
        r = '<div style="text-align:right;"><small>'+(' | '.join(val))+'</small></div>'
    return r

class JSONRequestHandler(BaseHTTPRequestHandler):
    view_url = '/view'

    def do_POST(self):
        auth_key = self.headers.get('Authentication')
        if args.KEY and args.KEY != auth_key:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'unauthorized')
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Get data
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()

        data = self.data_string.decode('utf8')
        data = json.loads(data)

        # Save data
        with open(args.FILE, 'a') as f:
            f.write(to_xml(data))


        # Response
        self.wfile.write(b'ok')
        return

    def do_GET(self):
        if self.path.startswith(self.view_url):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes('<html><head><title>Title goes here.</title><meta charset="utf-8"></head><style>a { text-decoration: none; color: inherit; }</style>','utf-8'))

            clips = from_disk()
            text = []
            tags = parse_qs(self.path).get(self.view_url + '?t')
            for d in clips:
                if tags is not None and len(set(d['tags']) & set(tags)) == 0:
                    continue
                item = []
                for k in ['quote', 'note', 'tags']:
                    vl = d[k] if d.get(k) is not None else d.get('clip') #NB: hack for back compat
                    if vl is None: continue
                    item.append(html_for_attribute(k, vl))
                href = d['dt_href'] if ('dt_href' in d and d['dt_href'] != '') else d['href'] if ('href' in d) else ''
                text.append('<a target="_blank" href="'+href+'" style="width:100%;">'+''.join(item)+'</a>')
            for t in text[::-1]:
                self.wfile.write(bytes(t, 'utf-8'))
                self.wfile.write(bytes('<hr/>', 'utf-8'))
            self.wfile.write(bytes('</html>','utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            self.wfile.write(bytes(feed_from_disk(),'utf-8'))


if __name__ == '__main__':
    print('Running on port', args.PORT)
    server = HTTPServer(("0.0.0.0", args.PORT), JSONRequestHandler)
    server.serve_forever()

