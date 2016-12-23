# -*- coding: utf-8 -*-

import cookielib, urllib, urllib2, re, sys

class VkontakteNotLoggedInError(Exception):
    pass

class VkontakteAuth:
    def __init__(self):
        self._vkontakte_cookie = cookielib.CookieJar()
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
        
        print >> sys.stderr, u"Logging in..."
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._vkontakte_cookie))

        host = 'http://login.vk.com/?act=login'
        post = urllib.urlencode({'email': login,
                                'expire': '',
                                'pass': password,
                                'vk': ''})

        try:
            conn = urllib2.Request(host, post)
            response = self._opener.open(conn)
            data = response.read()

            id_match = re.findall(r"id: (\d+),", data)
            if len(id_match) > 0:
                self._vkontakte_id = int(id_match[0])
                                    
            if self._vkontakte_id != -1:
                self._logged_in = True
                print >> sys.stderr, u"done (%s)." % self._vkontakte_id
            else:
                print >> sys.stderr, u'Incorrect id: wrong password?'
                
        except urllib2.URLError, e:
            if e.code == 403:
                print >> sys.stderr, u'Unexpected response status: wrong password?'
            else:
                print >> sys.stderr, u'URLError happen %s' % e

        return self._logged_in
    