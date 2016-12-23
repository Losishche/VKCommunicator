import urllib, urllib2, re, sys
import vkontakte.auth
from vkontakte.common import unescape

class FriendsFetcher:
    def __init__(self, vkontakte_auth):
        self._auth = vkontakte_auth
        self._friends_list = []
        
    def fetch_list(self):
        print >> sys.stderr, u'fetching friends list...'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._auth.get_cookie()))
        post = urllib.urlencode({'act': 'load_friends_silent',
                                 'al': '1',
                                 'gid': '0',
                                 'id': str(self._auth.GetID())})
        request = urllib2.Request('http://vkontakte.ru/al_friends.php', post)
        response = opener.open(request)
        udata = unicode(response.read(), 'windows-1251')
        #print >> sys.stderr, udata
        self._friends_list = re.findall(r'\[\'(\d+)\',\'.*?\',\'.*?\',\'.*?\',\'(.*?)\'', udata)
        print >> sys.stderr, u"done (%d friends)." % len(self._friends_list)
        
    def GetFriends(self):
        if len(self._friends_list) == 0:
            self.fetch_list()
        
        return self._friends_list
            
    