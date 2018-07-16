__author__ = 'grishaev'
from selenium import webdriver

import http.cookiejar, re, sys, logging
from urllib import request, parse
import urllib
import time

logging.basicConfig(level = logging.DEBUG, filename = 'vklog') # при активации параметра логи пишутся в файл)



class VkontakteNotLoggedInError(Exception):
    pass

class VkontakteAuth:
    def __init__(self):
        self._vkontakte_cookie = http.cookiejar.CookieJar()
        self._logged_in = False
        self._vkontakte_id = -1

    def get_cookie(self):
        if not self.IsLoggedIn():
            raise VkontakteNotLoggedInError()
        return self._vkontakte_cookie;

    def IsLoggedIn(self):
        return self._logged_in

    def GetID(self):
        return self._vkontakte_id

    def Login(self, login, password):
        self._vkontakte_id = -1
        self._logged_in = False

        print(sys.stderr, u"Logging in...") # как изменять направление вывода
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._vkontakte_cookie))

        host = 'http://login.vk.com/?act=login'
        post = parse.urlencode({'email': login,
                                'expire': '',
                                'pass': password,
                                'vk': ''})

        try:
            conn = urllib2.Request(host, post)
            response = self._opener.open(conn)
            data = response.read()
            logging.debug(data)

            id_match = re.findall(r"id: (\d+),", data)
            logging.debug(id_match)
            if len(id_match) > 0:
                self._vkontakte_id = int(id_match[0])

            if self._vkontakte_id != -1:
                self._logged_in = True
                print(sys.stderr, u"done (%s)." % self._vkontakte_id)
            else:
                print(sys.stderr, u'Incorrect id: wrong password?')

        except urllib2.URLError:
            e= None #todo
            if e.code == 403:
                print(sys.stderr, u'Unexpected response status: wrong password?')
            else:
                print(u'URLError happen %s' % e)

        return self._logged_in


def drv(login, password, auth_url = 'https://vk.com/login', url_for_token=None, delay=14):
    #todo брать из браузера токен автоматически
    chrome_browser = webdriver.Chrome('/home/grishaev/PycharmProjects/VKSpammer/WebDriver/chromedriver')
    #_vkontakte_cookie = http.cookiejar.CookieJar()
    #print(dir(_vkontakte_cookie))
    #_opener = request.build_opener(request.HTTPCookieProcessor(_vkontakte_cookie))
    #print(_vkontakte_cookie)
    #post = parse.urlencode({'email': 'agr39@ya.ru',
                     # 'expire': '',
                      # 'pass': 'ukfd,e[11',
                      # 'vk': ''
    #})
    #print(post)
    #response = request.Request(auth_url, post)
    #print(response)
    #chrome_browser.add_cookie(_vkontakte_cookie._cookies_for_request())
    chrome_browser.get(auth_url)
    elem_for_email = chrome_browser.find_element_by_id("email")
    elem_for_pass = chrome_browser.find_element_by_id("pass")
    #print(dir(chrome_browser))
    print(elem_for_pass, elem_for_email)
    elem_for_email.send_keys(login)
    elem_for_pass.send_keys(password)
    elem_for_email.submit()
    time.sleep(delay)
    chrome_browser.get(url_for_token)
    unparsed_token = chrome_browser.current_url
    print(unparsed_token)
    #time.sleep(300)
    return unparsed_token

    #elem_for_logout = chrome_browser.find_elements_by_id()

    #print(dir(chrome_browser))
    #print(chrome_browser.get(auth_url))

def get_token_by_inner_driver(drv):
    pass


if __name__ == '__main__':
    drv()