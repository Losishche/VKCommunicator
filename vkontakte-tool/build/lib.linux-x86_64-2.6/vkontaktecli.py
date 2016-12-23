#!/usr/bin/env python
# -*- coding: UTF8 -*-
import getopt, sys, os
import locale

import vkontakte.auth
import vkontakte.friends
import vkontakte.groups
import vkontakte.graffiti

def check_login(login, password):
    auth = vkontakte.auth.VkontakteAuth()
    success = auth.Login(login, password)
    if success:        
        return auth
    else:
        return False
    
    #type = friends или groups
def list(auth, list_type):
    assert list_type in ['friends', 'groups', 'accepted_groups']
    if list_type == 'friends':
        friends = vkontakte.friends.FriendsFetcher(auth)
        for (fid, name) in friends.GetFriends():
            print u"id: %d,\tИмя: %s" % (int(fid), name)
    elif list_type == 'groups':
        groups = vkontakte.groups.GroupsFetcher(auth)
        for (gid, name) in groups.GetGroups():
            print u"id: %d,\tНазвание: %s" % (int(gid), name)
    elif list_type == 'accepted_groups':
        groups = vkontakte.groups.GroupsFetcher(auth)
        for (gid, name) in groups.GetAcceptedGroups():
            print u"id: %d,\tНазвание: %s" % (int(gid), name)            
            
def graffiti(auth, graffiti_type, graffiti_id, graffiti_image):
    assert graffiti_type in ['friend', 'group']
    
    vkontakte_graffiti = vkontakte.graffiti.Graffiti(auth)
    vkontakte_graffiti.LoadImage(graffiti_image)
    (url, sentas) = vkontakte_graffiti.PostImage(graffiti_type, graffiti_id, vkontakte.graffiti.SENDAS_PNG_JPEG)
    
    if sentas == vkontakte.graffiti.SENDAS_JPEG:
        fmt = u"JPEG"
    elif sentas == vkontakte.graffiti.SENDAS_PNG:
        fmt = u"PNG"
    else:
        fmt = u"UNKNOWN"
        
    print u"Графити загружено успешно в формате %s: %s" % (fmt, url)
    

def usage():
    print u"""
    %s -l email -p пароль [действие [аргументы]]
    Если действие не указано, проверяет возможность входа на сайт с указанными данными.
    
    Поддерживаемые действия:
    list friends | groups | accepted_groups
    выводит список "друзей", "групп", "подтвержденных групп" вместе с идентификаторами
    
    graffiti friend | group id путь_к_изображению
    загружает на стену друга или группы изображение
    """ % sys.argv[0]

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "l:p:", ["login=", "password="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(-1)
    
    login = ''
    password = ''
    
    for o, a in opts:
        if o in ("-l", "--login"):
            login = a
        elif o in ("-p", "--password"):
            password = a        
        else:
            assert False, "Неизвестный параметр"
    
    if login == '':
        usage()
        sys.exit(-1)
        
    if password == '':
        usage()
        sys.exit(-1)
    
    if len(args) < 1:
        action = 'check'
    else:
        action = args[0]
        
    if action not in ['list', 'graffiti', 'check']:
        usage()
        sys.exit(-1)
    
    if action == 'list':
        list_arg = args[1]
        if list_arg not in ['friends', 'groups', 'accepted_groups']:
            usage()
            sys.exit(-1)                    
    elif action == 'graffiti':
        if len(args) < 4:
            usage()
            sys.exit(1)
            
        graffiti_arg = args[1]
        if graffiti_arg not in ['friend', 'group']:
            usage()
            sys.exit(-1)
        try:
            graffiti_id = int(args[2])
        except ValueError:
            usage()
            sys.exit(-1)
            
        if graffiti_id <= 0:
            usage()
            sys.exit(-1)
            
        graffiti_image = args[3].decode(locale.getpreferredencoding())        
        if not os.access(graffiti_image, os.F_OK):
            print u"Файл не найден: %s" % graffiti_image
            usage()
            sys.exit(-1)        

    #конец проверки опций
    
    try:
        vkontakte_auth = check_login(login, password)
        if not vkontakte_auth:
            print u"Вход не удался (неверный пароль?)"
            sys.exit(1)

        if action == 'check':
            print u"Вход удался (id = %d)" % vkontakte_auth.GetID()
            sys.exit(0)
        
        if action == 'list':
            list(vkontakte_auth, list_arg)
        elif action == 'graffiti':
            graffiti(vkontakte_auth, graffiti_arg, graffiti_id, graffiti_image)
    
    except Exception, e:
        print u"Произошла ошибка:"
        print e
        
if __name__ == "__main__":
    main()
