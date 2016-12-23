__author__ = 'grishaev'


import logging

import re
from io import BytesIO
from wsgiref.simple_server import make_server
from urlparse import urljoin, urlparse, ParseResult

import requests
from lxml import html, etree

log = logging.getLogger("habraproxy")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

HABRA_URL = 'http://habrahabr.ru'


def main():
    log.info("Running server...")
    make_server("", 8010, HabraProxy(HABRA_URL)).serve_forever()


class RedirectError(requests.HTTPError):
    pass


class MethodError(requests.HTTPError):
    pass


class HabraProxy(object):

    htmlcontent = 'text/html'

    def __init__(self, baseurl):
        self.baseurl = baseurl

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        remote_url = urljoin(self.baseurl, path)

        try:
            if 'GET' not in method:
                raise MethodError

            r = requests.head(remote_url)
            content_type = r.headers['content-type']
            if r.status_code != 200 \
                    or self.htmlcontent not in content_type:
                raise RedirectError

            status = b"%s %s" % (r.status_code, r.reason)
            length, buf = self.parse_html(remote_url, r.encoding)

            start_response(status, [
                (b'Content-Type', content_type),
                (b'Content-Length', length),
            ])
            return buf

        except RedirectError:
            r = requests.get(remote_url, stream=True)
            status = b"%s %s" % (r.status_code, r.reason)
            content_encoding = r.headers.get('content-encoding', b'')
            start_response(status, [
                (b'Content-Type', content_type),
                (b'Content-Encoding', content_encoding),
            ])
            return r.raw
        except MethodError:
            status = b'405 Method Not Allowed'
            headers = [(b"Content-type", b'text/plain')]
            start_response(status, headers)
            return [b"Posting is not supported by this proxy"]
        except requests.ConnectionError:
            status = b'500 Internal Server Error'
            headers = [(b"Content-type", b'text/plain')]
            start_response(status, headers)
            return [b"Check your Internet connection"]

    def parse_html(self, remote_url, encoding):
        doc = html.parse(remote_url)
        habra_parse_root(doc.getroot())
        buf = BytesIO()
        doc.write(buf, encoding=encoding, method="html")
        length = b"%s" % buf.tell()
        buf.seek(0)
        return length, buf


def tm_encode(source):
    if not source.strip():
        return source
    tm_symbol = "\u2122"
    return re.sub(r"(\b\w{6}\b)", r"\1%s" % tm_symbol, source,
                  flags=re.UNICODE)

UNTOUCHABLE_TAGS = set(('code', 'script', 'style'))


def habra_parse_root(root, baseurl=HABRA_URL):
    for tag in root.iter(tag=etree.Element):
        check_tags = set([el.tag for el in tag.iterancestors()] + [tag.tag])
        if not check_tags & UNTOUCHABLE_TAGS:
            if tag.text:
                tag.text = tm_encode(tag.text)
            if tag.tail:
                tag.tail = tm_encode(tag.tail)
        if tag.tag == 'a':
            href = tag.get('href')
            if href is not None:
                tag.attrib['href'] = relative_href(href, baseurl)


def relative_href(href, baseurl):
    pr_href = urlparse(href)
    if not pr_href.netloc:
        return href
    pr_base = urlparse(baseurl)
    if not pr_base.netloc == pr_href.netloc:
        return href
    return ParseResult('', '', *pr_href[2:]).geturl()


if __name__ == '__main__':
    main()