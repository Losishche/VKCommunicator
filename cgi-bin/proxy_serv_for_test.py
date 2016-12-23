__author__ = 'grishaev'

import socket
import requests
from  urllib.parse import urljoin, urlparse, ParseResult
import lxml.html as html
from lxml import etree
from xml.etree.ElementTree import ElementTree
import lxml
import time
import cgi
import re
from io import StringIO, BytesIO


class InnerServerConnections():
    #todo оформить классы соединений и сокетов через наследование!!!

    pattern_for_re = bytes('<div class="content html_format">', encoding='utf-8')
    pattern_for_re_out = '</div>'

    def __init__(self, port, count_of_client=2):

        self.port =port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        self.sock.listen(count_of_client) #параметр - допустимое количество клиентов в очереди
        print('open socket with port: {}'.format(self.port))

    @staticmethod
    def relative_href(href, main_domain_patt):
        pr_href = urlparse(href)
        if not pr_href.netloc:
            return href
        pr_base = urlparse(main_domain_patt)
        if not pr_base.netloc == pr_href.netloc:
            return href
        return ParseResult('', '', *pr_href[2:]).geturl()


    def replace_word_with_tm(self, word):

        if not word.strip():
            print("не меняем ", word.strip())
            return word
        res = re.sub(r'(\b[^\-]\w{6}\b)', r'\1{0}'.format('\N{TRADE MARK SIGN}'), word, flags=re.VERBOSE)
        return res


    def accept_and_handle_client(self, timeout=60, main_domain_patt='http://habrahabr.ru{}'):

        #sys.stdout = flushfile(sys.stdout) #перенаправляем вывод в файл!!!!

        state = True
        while state:
            self.conn, self.addr = self.sock.accept()
            print('accepting ', self.port)
            self.conn.settimeout(timeout)
            self.data = self.conn.recv(1024)
            self.data= self.data.decode('utf8')
            lis = self.data.split('\n')
            http_query_path = lis[0].split()[1]
            #print(lis)
            print(http_query_path)
            print('тут пусто?', self.data)
            if self.data and http_query_path[-1] == '/':
                url_for_proxing = 'http://habrahabr.ru{}'.format(http_query_path)
                result = requests.request('get', 'http://habrahabr.ru{}'.format(http_query_path))
                r = requests.head(url_for_proxing)
                print(dir(result))
                content = result.content
                #todo

                #exp_again_tree = html.fromstring(content)
                #tex = exp_again_tree.text_content()
                result_exp_again = re.sub(r'(\b\w{6}\b)', r'\1{0}'.format('\N{TRADE MARK SIGN}'), content.decode('utf8'),flags=re.UNICODE)
                #exp_again_tree.replace(exp_again_tree, result_exp_again)

                habr_elem_tree = html.parse(StringIO(content.decode('utf8')))
                #print(help(habr_elem_tree.write))
                #habr_elem_tree = result_exp_again
                #result_exp_again = html.tostring(habr_elem_tree)
                #habr_tree = html.fromstring(content)
                rt = habr_elem_tree.getroot()
                #print(help(habr_tree.findall))
                print(rt, habr_elem_tree)
                print(dir(habr_elem_tree))


                for elem in rt.iter(tag=etree.Element):
                    #print('есть ли текст?', tag.text)
                    #check_tags = set([el.tag for el in tag.iterancestors()] + [tag.tag])
                    #if tag: #not check_tags:
                    if elem.text:
                        elem.text = self.replace_word_with_tm(elem.text)

                    if elem.tail:
                        elem.tail = self.replace_word_with_tm(elem.tail)

                    if elem.tag == 'a':
                        href = elem.get('href')
                        if href is not None:
                            elem.attrib['href'] = self.relative_href(href, main_domain_patt)

                buf = BytesIO()
                habr_elem_tree._setroot(rt)
                habr_elem_tree.write(buf, method="html")
                buf.seek(0, 0)
                #print('есть?', buf)

            else:
                result = requests.request('get', 'http://habrahabr.ru{}'.format(http_query_path))
                content = result.content
                #print(content)
            #print(help(self.conn))

            #print(buf)
            for line in buf:
                print(line.decode('utf8'))
                self.conn.send(line)
                #time.sleep(60)
            print('послали контент')
                #self.data = self.conn.recv(1024)
            self.conn.send('200'.encode('utf8'))
            self.conn.close()
            print('закрыли подключение')


serv_instance =  InnerServerConnections(8233)
serv_instance.accept_and_handle_client()






