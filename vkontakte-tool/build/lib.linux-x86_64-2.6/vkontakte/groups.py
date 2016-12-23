import urllib, urllib2, re, sys
import vkontakte.auth
from vkontakte.common import unescape

class GroupsFetcher:
    def __init__(self, vkontakte_auth):
        self._auth = vkontakte_auth
        self._groups_list = []
        self._accepted_groups_list = []        
        
    def fetch_list(self):
        print >> sys.stderr, u'fetching groups list...'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._auth.get_cookie()))
        post = urllib.urlencode({'act': 'get_list',
                                 'al': '1',
                                 'al_ad': '1',
                                 'mid': str(self._auth.GetID()),
                                 'tab': 'groups'})
        request = urllib2.Request('http://vkontakte.ru/al_groups.php', post)
        response = opener.open(request)
        udata = unicode(response.read(), 'windows-1251')
        #print >> sys.stderr, udata
        self._groups_list = re.findall(r'\["(.+?)",\d*,(\d+),', udata)
        
        #reversing all touples inside a group_list and unescape them
        self._groups_list = [(gid, unescape(name)) for name, gid in self._groups_list]
        
        #for (gid, name) in self._groups_list:
        #    if not re.search("processRequest\(%s" % gid, udata):
        #        self._accepted_groups_list += [(gid, name)]
        
        #temporary equal this before i will know, how unaccepted groups looks like
        self._accepted_groups_list = self._groups_list
        
        print >> sys.stderr, u"done (%d/%d groups)." % (len(self._accepted_groups_list), len(self._groups_list))
        
    def GetGroups(self):
        if len(self._groups_list) == 0:
            self.fetch_list()
        
        return self._groups_list
    
    def GetAcceptedGroups(self):
        if len(self._accepted_groups_list) == 0:
            self.fetch_list()
            
        return self._accepted_groups_list
    