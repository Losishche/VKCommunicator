import urllib2, re, sys
import vkontakte.auth
from vkontakte.common import unescape

class FriendsFetcher:
    def __init__(self, vkontakte_auth):
        self._auth = vkontakte_auth
        self._friends_list = []
        
    def fetch_list(self):
        print >> sys.stderr, u'fetching friends list...'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._auth.get_cookie()))
        response = opener.open('http://vkontakte.ru/friends.php')
        data = response.read()        
        udata = unescape(unicode(data, 'windows-1251'))
        #print >> sys.stderr, udata
        f = re.findall(r'\[\'(\d+)\',\'.*?\',\'.*?\',\'.*?\',\'(.*?)\'', udata)
        self._friends_list = f
        print >> sys.stderr, u"done (%d friends)." % len(f)
        
    def GetFriends(self):
        if len(self._friends_list) == 0:
            self.fetch_list()
        
        return self._friends_list
            
    