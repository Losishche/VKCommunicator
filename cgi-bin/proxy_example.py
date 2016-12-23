#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function


#  habraproxy.py — это простейший http-прокси-сервер, запускаемый локально
#  (порт на ваше усмотрение), который показывает содержимое страниц Хабра. С
#  одним исключением: после каждого слова из шести букв должен стоять значок
#  «™». Примерно так:
#
#  http://habrahabr.ru/company/yandex/blog/258673/
#  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Сейчас на фоне уязвимости
#  Logjam все в индустрии в очередной раз обсуждают проблемы и особенности TLS.
#  Я хочу воспользоваться этой возможностью, чтобы поговорить об одной из них,
#  а именно — о настройке ciphersiutes.
#
#  http://127.0.0.1:8232/company/yandex/blog/258673/
#  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Сейчас™ на фоне уязвимости
#  Logjam™ все в индустрии в очередной раз обсуждают проблемы и особенности
#  TLS. Я хочу воспользоваться этой возможностью, чтобы поговорить об одной из
#  них, а именно™ — о настройке ciphersiutes.
#
#  Условия: * Python 2.x * можно использовать любые общедоступные библиотеки,
#  которые сочтёте нужным * чем меньше кода, тем лучше. PEP8 — обязательно * в
#  случае, если не хватает каких-то данных, следует опираться на здравый смысл
#
#  Если задача кажется слишом простой, можно добавить следующее: * параметры
#  командной строки (порт, хост, сайт, отличный от хабра и т.п.) * после старта
#  локального сервера автоматически запускается браузер с открытой
#  обработанной™ главной страницей

import logging

import re
from io import BytesIO, StringIO
from wsgiref.simple_server import make_server
from  urllib.parse import urljoin, urlparse, ParseResult

import requests
from lxml import html, etree

log = logging.getLogger("habraproxy")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

HABRA_URL = 'http://habrahabr.ru'


def main():
    log.info("Running server...")
    make_server("", 8233, HabraProxy(HABRA_URL)).serve_forever()


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
                pass
                #raise RedirectError

            status = "{} {}".format(r.status_code, r.reason)
            status = status.encode('utf8')
            length, buf = self.parse_html(remote_url, r.encoding)

            start_response(status, [
                ('Content-Type', content_type),
                ('Content-Length', length),
            ])
            return buf

        except RedirectError:
            r = requests.get(remote_url, stream=True)
            status = "{} {}".format(r.status_code, r.reason)
            status = status.encode('utf8')
            content_encoding = r.headers.get('content-encoding', '')
            start_response(status, [
                ('Content-Type', content_type),
                ('Content-Encoding', content_encoding),
            ])
            return r.raw
        except MethodError:
            status = '405 Method Not Allowed'
            headers = [("Content-type", 'text/plain')]
            start_response(status, headers)
            return ["Posting is not supported by this proxy"]
        except requests.ConnectionError:
            status = '500 Internal Server Error'
            headers = [("Content-type", 'text/plain')]
            start_response(status, headers)
            return [b"Check your Internet connection"]

    def parse_html(self, remote_url, encoding):
        doc = html.parse(StringIO(remote_url))
        habra_parse_root(doc.getroot())
        buf = BytesIO()
        doc.write(buf, encoding=encoding, method="html")
        length = "%s" % buf.tell()
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
