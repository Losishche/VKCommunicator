#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'grishaev'

from multiprocessing import cpu_count
print("число процессоров = {}".format( cpu_count()))

from app_info import final_sending_privat_message
from app_info import get_token, get_ava_id_and_insert_in_into_db
from app_info import connection_to_postgres
from app_info import get_token_from_db_bot
from multiprocessing import Process, Queue
#from work_with_DB import select_for_update
import vk
from app_info import get_auth_params, get_api

def execute(queue, offset, api):

    postgres_con, postgres_cur = connection_to_postgres()
    #n - оффсет!!! указывать обязательно
    proc = final_sending_privat_message(api, postgres_con, postgres_cur, 'roxbury', offset)


#queue = Queue()
allProcess = []

bots_id_tuple = (
    '367999823',
    '368514350',
    '375638959',
    '376081492',
    '377659979'
)

# проблема! обращается к одной и той же таблице, в которой выбгребание записей происходит попорядку
# и поэтому, выгребается всегда первая строчка
# для решения сделали оффсеты
def sender_in_privat_with_multiproc(offset=0):
    """

    :param offset: смещение для функции отправки сообщений (для каждого подпроцесса задается стартовое
    смещение номера пользователя, которым будут отправлены сообщения. ДОЛЖЕН БЫТЬ синхронизирован с count отправки
    сообщений в функции отправки, ИНАЧЕ БУДУТ ДУБЛИ СООБЩЕНИЙ!!!)
    :return:
    """

    for user_id in bots_id_tuple:
        #print('необходимо разлогиниться, удалить файл с токеном и залогиниться заново.'
              #'Как будет сделано, введите "у"')
        #yes = input()
        yes = 'y'
        if yes == 'y':
            api = get_token_from_db_bot(user_id) #функция для получения токена из "базы ботов" (объекта shelve)
            #api = get_token() для старой версии без shelve!!!!
            p = Process(target = execute, args=(queue, offset, api))
            allProcess.append(p)
            #p.start()
            print('создали!')
            offset += 10
    print(allProcess)

    for p in allProcess:

        p.start()





if __name__ =='__main__':
    sender_in_privat_with_multiproc()