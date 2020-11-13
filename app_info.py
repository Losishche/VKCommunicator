from __future__ import unicode_literals
import requests
import json
from urllib.parse import parse_qs
import webbrowser
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import pickle
from datetime import datetime, timedelta
from work_with_DB import select_group_users_union_from_inner_db_FOR_UPDATE, select_vk_errors
import vk
import time
import random
from PIL import Image
from io import BytesIO
from multiprocessing import Process

import psycopg2
import settings
import logging
import shelve
import os
from django import db

# -*- coding: utf-8 -*-

# версия api вКонтакте
api_vk_version = 5.21

# нумерация приложений идёт в обратном порядке
app_id_1 = 5556034  # идентификатор приложения
app_name_1 = 'CommonApp'
protected_key_2 = 'F0eYCZDPxh4rtawBEca5'

app_id_2 = 5813739
app_name_2 = 'CommonAppTest1'
protected_key_3 = 'WfQQUqkFU5JYj7UbmMfB'

app_id = 5786026
protected_key = 'jS8ah0U0wlHiw5h252ZJ'

proccess_log_file_path = \
    '/home/grishaev/PycharmProjects/VKSpammer/VKSpammer/VKSpam_djg/static/VKSpam_djg/process_log.txt'
chromeDriverPath = '/home/grishaev/PycharmProjects/VKSpammer/WebDriver/chromedriver'
logger = logging.getLogger('logger_for_communicator')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(proccess_log_file_path)
fh.setLevel(logging.INFO)
logger.addHandler(fh)

# инициализация файла c ботами
if os.path.exists('.db_vk_bots') is not True:
    db = shelve.open('.db_vk_bots', 'c')
    db.close()


def connection_to_postgres():
    # ДОДЕЛАТЬ!!!
    psycopg2.threadsafety = 3
    # todo дублирование кода! аналогичная ф-я  есть в work_with_DB
    connection_string = "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(
        settings.postgres_database_settings['HOST'],
        settings.postgres_database_settings['DB'],
        settings.postgres_database_settings['USER'],
        settings.postgres_database_settings['PASSWORD']
    )
    postgres_con = psycopg2.connect(
        connection_string
    )
    # print(dir(psycopg2))
    print("объект подключения", postgres_con)
    # postgres_con.set_isolation_level(0)
    postgres_cur = postgres_con.cursor()
    return postgres_con, postgres_cur


def multiconnection_to_postgres(count_of_connections):
    # ДОДЕЛАТЬ!!!
    # psycopg2.threadsafety = count_of_connections
    list_postgres_con = []
    # postgres_con = psycopg2.connect(
    #    "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(settings.postgres_database_settings['HOST'],
    #                                                               settings.postgres_database_settings['DB'],
    #                                                           settings.postgres_database_settings['USER'],
    #                                                               settings.postgres_database_settings['PASSWORD']),
    # sslmode='disable')

    list_postgres_cur = []
    for i in range(count_of_connections):
        postgres_con = psycopg2.connect(
            "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(
                settings.postgres_database_settings['HOST'],
                settings.postgres_database_settings['DB'],
                settings.postgres_database_settings['USER'],
                settings.postgres_database_settings['PASSWORD'])
        )
        list_postgres_con.append(postgres_con)
        list_postgres_cur.append(postgres_con.cursor())
    return list_postgres_con, list_postgres_cur


def upd_cursor_for_postgres(conn, cur):
    cur.close()
    conn.cursor()
    return conn.cursor()


def make_and_do_insert_records_to_cities(postgres_con, postgres_cur, list_of_dict_cities):
    """
    записывает города из VK в базу. По сути одноразовая вспомогательная ф-я
    в кортеже необходимо всегда передавать регион (нужно учитывать, что апи VK не возвращает регион для некоторых городов)
    :param postgres_con:
    :param postgres_cur:
    :param list_of_dict_cities:
    :return:
    """

    for city in list_of_dict_cities:
        if city.get('region') is None:
            city['region'] = city['title']

    query = '''
        insert into cities(vk_cid, title, region)
        values (%(cid)s, %(title)s, %(region)s)
    '''

    try:
        print(list_of_dict_cities)
        # print(help(postgres_cur.executemany))
        postgres_cur.executemany(query, list_of_dict_cities)
        # postgres_cur.execute(query)
        postgres_con.commit()
        if postgres_cur.statusmessage != 0:
            return str(postgres_cur.statusmessage)
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА ЗАПИСИ В БД VKSpammer'))


def insert_records_to_vk_group_user(postgres_con, postgres_cur, tupl_member_of_group):
    # можно охренеть, но в типах данных ТУТ именно ДОЛЖНЫ быть строки, независимо от фактического типа!
    query = '''
            INSERT into vk_group_user(vk_id, last_name, can_write_private_message, first_name)
            VALUES (%(uid)s, %(last_name)s, %(can_write_private_message)s, %(first_name)s)
        '''

    try:
        print(tupl_member_of_group)
        print(tupl_member_of_group[122]['uid'])
        # print(help(postgres_cur.executemany))
        postgres_cur.executemany(query, tupl_member_of_group)
        # postgres_cur.execute(query)
        postgres_con.commit()
        if postgres_cur.statusmessage != 0:
            return str(postgres_cur.statusmessage)
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА ЗАПИСИ В БД VKSpammer'))


def make_insert_records_to_vk_group_user_union(postgres_con, postgres_cur, tupl_member_of_group, group_id):
    """
    делает инсерт пользователей группы в таблицу платформы
    в текущей версии, проверяет есть ли пользователь уже в БД, если есть, не добавляет его в список для инсерта
    """
    # выдергиваем существующие записи из БД и сравниваем
    temp_list = []
    query_for_select_existing_records = '''
        SELECT * FROM vk_group_user_union_2
    '''
    # todo  ДОДЕЛАТЬ!! Cделать выдергивание существующих записей по оффсетам!!
    try:
        postgres_cur.execute(query_for_select_existing_records)
        result = postgres_cur.fetchall()
        # print(result)
        if postgres_cur.statusmessage != 0:
            print(str(postgres_cur.statusmessage))
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА ЧТЕНИЯ БД VKSpammer'))
        # todo изменить на генерацию исключения и проверить
        return 'error'

    vk_user_ids = []
    for item in result:
        vk_user_ids.append(item[1])
    lis_member_of_group = list(tupl_member_of_group)

    for member in lis_member_of_group:
        if member.get('uid') in vk_user_ids:  # может быть другой ключ??
            print('повторяющийся пользователь', member)
            # если есть в списке-ответе БД, то НЕ ДОБАВЛЯЕМ!!
            continue
        # todo описать логику!!!!
        if member.get('city') is None:
            member['city'] = None
        if member.get('bdate') is None:
            member['bdate'] = None
        elif len(member.get('bdate')) not in [8, 9, 10]:
            member['bdate'] = None
        elif str(member.get('bdate')) == '31.2.1920':
            member['bdate'] = None

        temp_list.append(member)
    # print(temp_list)
    # вконтакт поменял формат поля city, пришлось сделать костыль
    for user_index in range(0, len(temp_list)):
        if(len(str(temp_list[user_index]['city']))) <= 30:
            temp_list[user_index]['city'] = str(temp_list[user_index]['city'])
        else:
            temp_list[user_index]['city'] = str(temp_list[user_index]['city']['id'])
    tupl_member_of_group = tuple(temp_list)

    # можно охренеть, но в типах данных ТУТ именно ДОЛЖНЫ быть строки, независимо от фактического типа!
    query = '''
            INSERT into vk_group_user_union_2(vk_id, last_name, can_write_private_message, first_name,
            sex, city, bdate, vk_group_id)
            VALUES (%(id)s, %(last_name)s, %(can_write_private_message)s, %(first_name)s,
             %(sex)s, %(city)s, %(bdate)s, '{}')'''.format(group_id)

    try:
        print(tupl_member_of_group)
        # print(tupl_member_of_group[122]['uid'])
        # print(help(postgres_cur.executemany))
        postgres_cur.executemany(query, tupl_member_of_group)
        # postgres_cur.execute(query)
        postgres_con.commit()
        if postgres_cur.statusmessage != 0:
            return str(postgres_cur.statusmessage)
    except psycopg2.IntegrityError as error:
        logging.warning('{}'.format('ОШИБКА ЗАПИСИ В БД VKSpammer'))
        logging.warning('{}'.format(error))


def make_insert_records_to_aim_group(postgres_con, postgres_cur, tupl_member_of_group_from_vk):
    """
    делает инсерт данных по целевой группе в таблицу платформы aim_group_id
    в текущей версии, проверяет есть ли пользователь уже в БД, если есть, не добавляет его в список для инсерта
    """
    # выдергиваем существующие записи из БД и сравниваем
    aim_group_id = 'gorkiy_group_user'
    temp_list = []
    query_for_select_existing_records = '''
        SELECT * FROM {}
    '''.format(aim_group_id)
    print(query_for_select_existing_records)
    # time.sleep(300)
    # todo  ДОДЕЛАТЬ!! Cделать выдергивание существующих записей по оффсетам!!
    try:
        response = postgres_cur.execute(query_for_select_existing_records)
        result = postgres_cur.fetchall()
        # print(result)
        if postgres_cur.statusmessage != 0:
            print(str(postgres_cur.statusmessage))
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА ЧТЕНИЯ БД VKSpammer'))
        return 'error'

    aim_group_user_ids = []
    for item in result:
        aim_group_user_ids.append(item[1])
    lis_member_of_group = list(tupl_member_of_group_from_vk)

    for member in lis_member_of_group:
        if member.get('uid') in aim_group_user_ids:  # может быть другой ключ??
            print('повторяющийся пользователь', member)
            # если есть в списке-ответе БД, то НЕ ДОБАВЛЯЕМ!!
            continue
        # todo описать логику!!!!
        if member.get('city') is None:
            member['city'] = None
        if member.get('bdate') is None:
            member['bdate'] = None
        elif len(member.get('bdate')) not in [8, 9, 10]:
            member['bdate'] = None

        temp_list.append(member)
    # print(temp_list)
    tupl_member_of_group = tuple(temp_list)
    print(tupl_member_of_group)
    # можно охренеть, но в типах данных для запроса в Postgres ТУТ именно ДОЛЖНЫ быть строки,
    # независимо от фактического типа!
    query = '''
            INSERT into {} (vk_id, last_name, can_write_private_message, first_name, sex, city, bdate)
            VALUES (%(uid)s, %(last_name)s, %(can_write_private_message)s, %(first_name)s,
             %(sex)s, %(city)s, %(bdate)s)'''.format(aim_group_id)
    print(query)
    # time.sleep(300)
    try:
        print(query)
        postgres_cur.executemany(query, tupl_member_of_group)
        # postgres_cur.execute(query)
        postgres_con.commit()
        if postgres_cur.statusmessage != 0:
            return str(postgres_cur.statusmessage)
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА ЗАПИСИ В БД VKSpammer'))
        return 'error'


def update_to_vk_group_user(postgres_con, postgres_cur, uid):
    query = '''
        UPDATE vk_group_user
        SET have_sent_messages = 'true'
        WHERE vk_id={}
    '''


def update_to_vk_group_user_union_ava_id(postgres_con, postgres_cur, avatar_id, vk_id, group_id=None):
    query = '''
        UPDATE vk_group_user_union_2
        SET avatar_id = {}
        WHERE vk_id={}
    '''
    try:
        postgres_cur.execute(query.format(avatar_id, vk_id))
        postgres_con.commit()
        if postgres_cur.statusmessage != 0:
            return str(postgres_cur.statusmessage)
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА ЗАПИСИ В БД VKSpammer'))


def update_to_vk_group_user_union_can_comment_ava(
        postgres_con, postgres_cur, avatar_id, vk_id, can_comment_ava, group_id=None
):
    query = '''
        UPDATE vk_group_user_union_2
        SET can_post_ava_comment = {}
        WHERE vk_id={} and avatar_id={}
    '''

    query2 = '''
        UPDATE vk_group_user_union_2
        SET can_post_ava_comment = {}, avatar_id=-1
        WHERE vk_id={}
    '''

    if can_comment_ava is True:
        try:
            postgres_cur.execute(query.format('true', vk_id, avatar_id))
            postgres_con.commit()
            if postgres_cur.statusmessage != 0:
                return str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ЗАПИСИ В БД VKSpammer'))
    else:
        print('отладка')
        try:
            postgres_cur.execute(query2.format('false', vk_id))
            postgres_con.commit()
            if postgres_cur.statusmessage != 0:
                return str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            print('ошибка записи?')
            logging.warning('{}'.format('ОШИБКА ЗАПИСИ В БД VKSpammer'))


def update_to_vk_photo_comment_state_group_user_union(postgres_con, postgres_cur, uid, can_post_ava_comment=True):
    """
    функция для обновления данных по аватаркам в БД
    :param postgres_con:
    :param postgres_cur:
    :param uid:
    :param can_post_ava_comment:
    :return:
    """
    if can_post_ava_comment is True:
        query = '''
            UPDATE vk_group_user_union_2
             SET have_post_photo_comment = true
             WHERE vk_id={}
        '''
        try:
            print(uid)
            # print(tupl_member_of_group[122]['uid'])
            # print(help(postgres_cur.execute))
            postgres_cur.execute(query.format(uid))
            postgres_con.commit()
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА АПДЕЙТА В БД VKSpammer'))
    else:
        # если возникает исключение, переписываем поле can_post_ava_comment в false
        query = '''
            UPDATE vk_group_user_union_2
             SET can_post_ava_comment = false
             WHERE vk_id={}
        '''
        try:
            print(uid)
            # print(tupl_member_of_group[122]['uid'])
            # print(help(postgres_cur.execute))
            postgres_cur.execute(query.format(uid))
            postgres_con.commit()
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА АПДЕЙТА В БД VKSpammer'))


def update_to_vk_wall_post_state_group_user_union(postgres_con, postgres_cur, uid, can_post_wall_comment=True):
    if can_post_wall_comment is True:
        query = '''
            UPDATE vk_group_user_union_2
             SET have_post_wall_comment = true
             WHERE id={}
        '''
        try:
            print(uid)
            # print(tupl_member_of_group[122]['uid'])
            # print(help(postgres_cur.execute))
            postgres_cur.execute(query.format(uid))
            postgres_con.commit()
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА АПДЕЙТА В БД VKSpammer'))
    else:
        # если возникает исключение, переписываем поле can_post_ava_comment в false
        query = '''
            UPDATE vk_group_user_union_2
             SET have_post_wall_comment = false
             WHERE id={}
        '''
        try:
            print(uid)
            # print(tupl_member_of_group[122]['uid'])
            # print(help(postgres_cur.execute))
            postgres_cur.execute(query.format(uid))
            postgres_con.commit()
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА АПДЕЙТА В БД VKSpammer'))


def update_to_vk_group_user_union(postgres_con, postgres_cur, uid, didnt_send=False):
    if didnt_send is False:
        query = '''
            UPDATE vk_group_user_union_2
             SET have_sent_messages = 'true'
             WHERE vk_id={}
        '''
        try:
            print(uid)
            # print(tupl_member_of_group[122]['uid'])
            # print(help(postgres_cur.execute))
            postgres_cur.execute(query.format(uid))
            postgres_con.commit()
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА АПДЕЙТА В БД VKSpammer'))
    else:
        query = '''
            UPDATE vk_group_user_union_2
             SET can_write_private_message = 0
             WHERE vk_id={}
        '''
        try:
            print(uid)
            # print(tupl_member_of_group[122]['uid'])
            # print(help(postgres_cur.execute))
            postgres_cur.execute(query.format(uid))
            postgres_con.commit()
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА АПДЕЙТА В БД VKSpammer'))


def update_to_vk_group_user_friend_added(postgres_con, postgres_cur, inner_uid):
    query = '''
        UPDATE vk_group_user_union_2
        SET added_to_friends = 'true'
        WHERE id={}'''
    try:
        print(inner_uid)
        postgres_cur.execute(query.format(inner_uid))
        postgres_con.commit()
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА АПДЕЙТА В БД VKSpammer'))


def select_group_users_from_inner_db(postgres_con, postgres_cur, group_id=0):
    query = '''
        SELECT * FROM vk_group_user
        WHERE have_sent_messages is not true and  can_write_private_message=1
        '''
    try:
        postgres_cur.execute(query)
        result = postgres_cur.fetchall()
        # print(result)
        if postgres_cur.statusmessage != 0:
            return result  # str(postgres_cur.statusmessage)
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def select_all_users_union_from_inner_db(postgres_con, postgres_cur, group_id=None):
    """
    SELECT ALL queries from users_union IF Without param group ID
    If it is asked just select users of asked group
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :return:
    """
    if group_id is None:
        query = '''
            SELECT * FROM vk_group_user_union_2
                WHERE have_sent_messages is not true and have_post_photo_comment is not true
                ORDER BY id
                '''
        try:
            logger.info('{}: we are using postgres_conn: {}'.format(datetime.now(), postgres_con))
            postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            # print(result)
            if postgres_cur.statusmessage != 0:
                return result  # str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))

    else:
        query = '''
            SELECT * FROM vk_group_user_union where vk_id={}
                WHERE have_sent_messages is not true and have_post_photo_comment is not true
                ORDER BY id
        '''
        try:
            postgres_cur.execute(query.format(group_id))
            result = postgres_cur.fetchall()
            # print(result)
            if postgres_cur.statusmessage != 0:
                return result  # str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def select_group_users_union_from_inner_db(postgres_con, postgres_cur, group_id=None):
    # todo разобраться с необходимостью условия в запросе!!! Видимо, это устарело!!!
    """
    выборка данных по пользователям групп из внутренней DB
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :return:
    """

    if group_id is None:
        query = '''
            SELECT * FROM vk_group_user_union_2
                WHERE have_sent_messages is not true and  can_write_private_message=1
                ORDER BY id
        '''
        try:
            logger.info('{}: we are using postgres_conn: {}'.format(datetime.now(), postgres_con))
            postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            # print(result)
            if postgres_cur.statusmessage != 0:
                return result  # str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))

    else:
        query = '''
            SELECT * FROM vk_group_user_union_2
                WHERE have_sent_messages is not true AND can_write_private_message=1
                AND vk_group_id='{}'
            '''.format(group_id)
        try:
            postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            # print(result)
            if postgres_cur.statusmessage != 0:
                return result  # str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def select_min_max_unhandled_id_gr_user_union(postgres_con, postgres_cur, group_id):
    """
    ВЫборка мин и макс ID ищ необработанных пользователей группы
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :return:
    """
    query_for_min = '''
        SELECT min(id) FROM vk_group_user_union_2
            WHERE have_sent_messages is not true
            AND can_post_ava_comment IS true
            AND have_post_photo_comment is not true
            AND have_post_wall_comment is not true
            AND vk_group_id='{}'
    '''.format(group_id)

    query_for_max = '''
        SELECT max(id) FROM vk_group_user_union_2
            WHERE have_sent_messages is not true
            AND can_post_ava_comment IS true
            AND have_post_photo_comment is not true
            AND have_post_wall_comment is not true
            AND vk_group_id='{}'
    '''.format(group_id)
    try:
        print(query_for_min)
        logger.info('{}: we are using postgres_conn: {}'.format(datetime.now(), postgres_con))
        response = postgres_cur.execute(query_for_min)
        min_id = postgres_cur.fetchall()[0][0]
        logger.debug('{}: response for min, {}'.format(datetime.now(), response))
        response = postgres_cur.execute(query_for_max)
        logger.debug('{}: response for max, {}'.format(datetime.now(), response))
        max_id = postgres_cur.fetchall()[0][0]
        print(min_id, max_id)
        return min_id, max_id
    except psycopg2.IntegrityError:
        print('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))
        logger.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def select_gr_users_union_from_inner_db_for_multiproc(postgres_con, postgres_cur, group_id, min_id, max_id):
    # todo фиг знает что тут за запрос!!!!
    """
    выборка данных по пользователям групп из внутренней DB ПО УСЛОВИЮ больше и меньше заданных ID
    для рассылки с мультипроцессингом
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :param min_id:
    :param max_id:
    :return:
    """
    query = '''
        SELECT * FROM vk_group_user_union_2
            WHERE
            have_sent_messages is not true
            AND can_post_ava_comment IS true
            AND have_post_photo_comment is not true
            AND have_post_wall_comment is not true
            AND vk_group_id='{}'
            AND id>='{}'
            AND id<'{}'
    '''.format(group_id, min_id, max_id)
    print(query)
    try:
        postgres_cur.execute(query)
        result = postgres_cur.fetchall()
        # print(result)
        # time.sleep(5)
        # print(result)
        if postgres_cur.statusmessage != 0:
            return result  # str(postgres_cur.statusmessage)
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def make_tuple_for_insert_record_to_vk_group_user(dict_res_members_of_group):
    tupl_member_of_group = tuple(dict_res_members_of_group['users'])
    return tupl_member_of_group


def select_users_info(postgres_con, postgres_cur, group_id=None, min_value=None, offset=None):
    if group_id:
        query = '''
            SELECT * FROM vk_group_user_union_2
            WHERE vk_group_id = '{}'
            '''.format(group_id)
        try:
            postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            # print(result)
            if postgres_cur.statusmessage != 0:
                return result  # str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))

    elif min_value and offset:
        query = '''
            SELECT * FROM vk_group_user_union_2
            WHERE vk_group_id = '{}' and id>='{}' limit '{}'
            '''.format(group_id, min_value, offset)
        try:
            postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            # print(result)
            if postgres_cur.statusmessage != 0:
                return result  # str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer при работе в режиме Мультисендер'))

    else:
        query = '''
            SELECT * FROM vk_group_user_union_2
        '''
        try:
            postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            # print(result)
            if postgres_cur.statusmessage != 0:
                return result  # str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def delete_duplicate_records_of_users_from_db(postgres_con, postgres_cur, users):
    """
    удаляет пользователей VK, которые уже есть в БД. Тупо удалает все повторения
    :param postgres_con:
    :param postgres_cur:
    :param users:
    :return:
    """
    # todo возможно следует сделать интеллектуальнее
    # todo возможно следует менять статусы данных а не удалять. Написать отдельную функцию для изменения статусов??

    template_query = 'delete from vk_group_user_union where id={}'
    duplicate_list = []
    user_dic = {}
    for user in users:
        if user_dic.get(user[1]):
            duplicate_list.append(user)
        else:
            user_dic[user[1]] = user[0]

    print(duplicate_list)
    print(len(duplicate_list))

    for id in duplicate_list:
        query = template_query.format(id[0])
        print(query)
        try:
            response = postgres_cur.execute(query)
            postgres_con.commit()
            # result = postgres_cur.fetchall()
            print(response)
            # time.sleep(300)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


############################################################################
############################################################################
############################################################################


def save_db_vk_bots(access_token, expires_in, user_id, filename='.db_vk_bots'):
    with shelve.open(filename) as db:
        expires = datetime.now() + timedelta(seconds=int(expires_in))
        db[user_id] = [access_token, expires]
        return 'OK'


def get_saved_auth_params_from_db_bots(user_id, filename='.db_vk_bots'):
    """
    Получает сохраненные токены пользователей из объекта shelve
    :param user_id:
    :param filename:
    :return:
    """
    access_token = None
    try:
        with shelve.open(filename) as db_file:
            # print(db_file.get(user_id))
            if db_file.get(user_id) is None:
                token_tmp = db_file[user_id][0]  # ?????
                expires = db_file[user_id][1]
                uid = user_id
                if datetime.now() < expires:
                    print(token_tmp, user_id)
                    access_token = token_tmp
                    user_id = uid
    except RuntimeError:
        print('не удалось прочитать файл')
        pass
    return access_token, user_id


# id of vk.com application
APP_ID = app_id
# file, where auth data is saved
AUTH_FILE = '.auth_data'
AUTH_FILE_2 = '../.auth_data'
# костылик для сохранения файла в разных местах.
# todo исправить работу view-функциий в DJANGo на работу с оригинальным файлом

# chars to exclude from filename
FORBIDDEN_CHARS = '/\\\?%*:|"<>!'


def get_saved_auth_params():
    """
    получение сохранённых настроек аутентификации (токен и т.д.)
    """
    access_token = None
    user_id = None
    try:
        with open(AUTH_FILE, 'rb') as pkl_file:
            token = pickle.load(pkl_file)
            expires = pickle.load(pkl_file)
            uid = pickle.load(pkl_file)
        if datetime.now() < expires:
            access_token = token
            user_id = uid
    except IOError:
        pass
    return access_token, user_id


# разобраться с юзер_id??
def save_auth_params(access_token, expires_in, user_id):
    expires = datetime.now() + timedelta(seconds=int(expires_in))
    with open(AUTH_FILE, 'wb') as output:
        pickle.dump(access_token, output)
        pickle.dump(expires, output)
        pickle.dump(user_id, output)
    with open(AUTH_FILE_2, 'wb') as output2:
        pickle.dump(access_token, output2)
        pickle.dump(expires, output2)
        pickle.dump(user_id, output2)


def save_multiple_auth_params_in_like_dict(access_token, expires_in, user_id):
    with open('.dict_auth_file', 'wb') as output:
        shelve.dump[user_id] = (access_token, expires_in)


def get_auth_params(flag=False, vk_app_list=None):
    """
    получение токена с сайта
    """
    if vk_app_list:
        # если передан список id приложений, выбираем приложение рандомно
        app_id = vk_app_list[random.randint(0, len(vk_app_list) - 1)]
        auth_url = ("https://oauth.vk.com/authorize?client_id={app_id}"
                    "&scope=wall,messages,audio,photos,groups, friends&redirect_uri=http://oauth.vk.com/blank.html"  # В ЭТОЙ СТРОКЕ ЗАПРОС НА ПРАВА ДОСТУПА К КОНТЕНТУ (scope)!!!
                    "&display=page&response_type=token".format(app_id=app_id))
    else:
        auth_url = ("https://oauth.vk.com/authorize?client_id={app_id}"
                    "&scope=wall,messages,audio,photos,groups, friends&redirect_uri=http://oauth.vk.com/blank.html"  # В ЭТОЙ СТРОКЕ ЗАПРОС НА ПРАВА ДОСТУПА К КОНТЕНТУ (scope)!!!
                    "&display=page&response_type=token".format(app_id=APP_ID)
                    )  # APP_ID - глобальная переменная с id приложения
    webbrowser.open_new_tab(auth_url)
    redirected_url = input("Paste here url you were redirected:\n")
    aup = parse_qs(redirected_url)
    aup['access_token'] = aup.pop('https://oauth.vk.com/blank.html#access_token')

    if flag is False:
        save_auth_params(aup['access_token'][0], aup['expires_in'][0], aup['user_id'][0])
    elif flag is True:
        save_db_vk_bots(aup['access_token'][0], aup['expires_in'][0], aup['user_id'][0])
    return aup['access_token'][0], aup['user_id'][0]


def get_auth_params_from_interface(vk_app_id=None):
    if vk_app_id:
        # если передан список id приложений, выбираем приложение рандомно
        app_id = vk_app_id
        print('идентификатор выпавшего приложения', app_id)
        # В ЭТОЙ СТРОКЕ ЗАПРОС НА ПРАВА ДОСТУПА К КОНТЕНТУ (scope)!!!
        # ВКОНТАКТ ВЫПИЛИЛ ПРАВО НА получение токена для messages ! поэтому его здесь нет!
        url_for_token = (
            "https://oauth.vk.com/authorize?client_id={app_id}"
            "&scope=wall,audio,photos,groups, friends&redirect_uri=http://oauth.vk.com/blank.html"
            "&display=page&response_type=token".format(app_id=app_id)
        )
    else:
        # В ЭТОЙ СТРОКЕ ЗАПРОС НА ПРАВА ДОСТУПА К КОНТЕНТУ (scope)!!!
        url_for_token = (
            "https://oauth.vk.com/authorize?client_id={app_id}"
            "&scope=wall,audio,photos,groups, friends&redirect_uri=http://oauth.vk.com/blank.html"
            "&display=page&response_type=token".format(app_id=APP_ID)
        )
    webbrowser.open_new_tab(url_for_token)


def get_token_by_inner_driver(login, password, auth_url='https://vk.com/login', delay=10, vk_app_list=None):
    """
    получение токена с сайта при работе через интерфейс с помощью драйвера браузера
    """
    # путь для запуска драйвера браузера
    chrome_browser = webdriver.Chrome(chromeDriverPath)
    if vk_app_list:
        # если передан список id приложений, выбираем приложение рандомно
        app_id = vk_app_list.get(id=random.randint(1, len(vk_app_list))).vk_app_id
        # В ЭТОЙ СТРОКЕ ЗАПРОС НА ПРАВА ДОСТУПА К КОНТЕНТУ (scope)!!!
        # ВКОНТАКТ ВЫПИЛИЛ ПРАВО НА получение токена для messages ! поэтому его здесь нет!
        url_for_token = ("https://oauth.vk.com/authorize?client_id={app_id}"
                         "&scope=wall,audio,photos,groups, friends&redirect_uri=http://oauth.vk.com/blank.html"
                         "&display=page&response_type=token".format(app_id=app_id)
                         )
    else:
        # В ЭТОЙ СТРОКЕ ЗАПРОС НА ПРАВА ДОСТУПА К КОНТЕНТУ (scope)!!!
        url_for_token = ("https://oauth.vk.com/authorize?client_id={app_id}"
                         "&scope=wall,audio,photos,groups, friends&redirect_uri=http://oauth.vk.com/blank.html"
                         "&display=page&response_type=token".format(app_id=APP_ID)
                         )
    chrome_browser.get(auth_url)
    elem_for_email = chrome_browser.find_element_by_id("email")
    elem_for_pass = chrome_browser.find_element_by_id("pass")
    # print(dir(chrome_browser))
    print(elem_for_pass, elem_for_email)

    elem_for_email.send_keys(login)
    elem_for_pass.send_keys(password)
    elem_for_email.submit()
    time.sleep(delay)
    chrome_browser.get(url_for_token)
    try:
        # find_elements_by_css_selector("allow(this);") #.
        elem_for_app_allow = chrome_browser.find_element_by_class_name("button_indent")
        print("найдена кнопка для разрешения приложения", elem_for_app_allow)
        print(dir(elem_for_app_allow))
        # time.sleep(300)
        time.sleep(delay - 7)
        elem_for_app_allow.click()
        time.sleep(delay - 7)
    except NoSuchElementException:
        print('кнопка разрешения не найдена')
    # input()
    unparsed_token = chrome_browser.current_url
    print(unparsed_token)
    # time.sleep(300)
    return unparsed_token
    # taken_drv = drv(url_for_token=auth_url)
    # taken_drv.get(auth_url)
    # headers = {'user-agent': 'my-app/0.0.1'}
    # r = requests.get(auth_url, headers=headers)
    # r.text


def parse_and_save_auth_params(redirected_url):
    """
    функция для парсинга токена из фронт энда и сохранения токена
    """
    aup = parse_qs(redirected_url)
    aup['access_token'] = aup.pop('https://oauth.vk.com/blank.html#access_token')
    save_auth_params(
        aup['access_token'][0],
        aup['expires_in'][0],
        aup['user_id'][0]
    )
    return aup['access_token'][0], aup['user_id'][0], aup['expires_in']


'''
def get_for_audio_token():
    auth_url = ("https://oauth.vk.com/authorize?client_id={app_id}"
                "&scope=wall,messages&redirect_uri=http://oauth.vk.com/blank.html"
                "&display=page&response_type=token".format(app_id=APP_ID))
    webbrowser.open_new_tab(auth_url)
    redirected_url = input("Paste here url you were redirected:\n")
    aup = parse_qs(redirected_url)
    aup['access_token'] = aup.pop(
        'https://oauth.vk.com/blank.html#access_token')
    save_auth_params(aup['access_token'][0], aup['expires_in'][0],
                     aup['user_id'][0])
    return aup['access_token'][0], aup['user_id'][0]
'''


def autentification_in_vk_via_web_dr(login, password, auth_url='https://vk.com/login', activity_time=300):
    """
    получение токена с сайта при работе через интерфейс
    """
    chrome_browser = webdriver.Chrome(chromeDriverPath)

    chrome_browser.get(auth_url)
    elem_for_email = chrome_browser.find_element_by_id("email")
    elem_for_pass = chrome_browser.find_element_by_id("pass")
    # print(dir(chrome_browser))
    print(elem_for_pass, elem_for_email)
    elem_for_email.send_keys(login)
    elem_for_pass.send_keys(password)
    elem_for_email.submit()
    time.sleep(activity_time)
    # return chrome_browser
    return 'OK'


def autentification_vk(app_id, protected_key, username, password):
    """
    первая часть функции - тоже самое получение токена!!! НО неограниченного по времени!
    :param app_id:
    :param protected_key:
    :param username:
    :param password:
    :return:
    """
    url = 'https://oauth.vk.com/token'
    params = {
        "grant_type": "password",
        "client_id": app_id,
        "client_secret": protected_key,
        "username": username,
        "password": password
    }
    headers = {'user-agent': 'my-app/0.0.1'}
    r = requests.get(url, headers=headers)

    opener = urllib2.build_opener(
        urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
        urllib2.HTTPRedirectHandler())
    print('ress', r.text)


def get_api(access_token):
    session = vk.Session(access_token=access_token)
    return vk.API(session)


def work_with_RuCaptcha() -> object:
    """
    :rtype : str
    """
    RU_captcha_app_key = 'e6659b185a261112373dc029c358f044'
    captcha_file = {'file': open('captcha_file.jpg', 'rb')}  # специально для последующего кодирования в запрос
    host = 'http://rucaptcha.com/in.php'
    data = {
        'method': 'post',
        'key': RU_captcha_app_key,
        # "file": captcha_file,
        "submit": "загрузить и получить ID",
    }
    res = requests.post(host, data, files=captcha_file)
    captcha_id = res.text[3:]
    print('xsx', res.text, captcha_id)
    res_host = 'http://rucaptcha.com/res.php?'
    res_data = {
        'key': RU_captcha_app_key,
        'action': 'get',
        'id': captcha_id
    }
    status = False
    pause_between_requests = 0
    step_for_increasing_pause = 5
    while not status:
        res_captcha = requests.get(res_host, res_data)
        if res_captcha.text == 'CAPCHA_NOT_READY':
            print(res_captcha.text)
            pause_between_requests += step_for_increasing_pause
            time.sleep(pause_between_requests)
        elif res_captcha.text[:2] == 'OK':
            print('разгаданная каптча', res_captcha.text)
            status = True
            # time.sleep(20)
            return res_captcha.text[3:]


# time.sleep(300)

def send_message(api, user_id, message, **kwargs):
    """
    фактическая отсылка сообщений (вспомогательная функция)
    :param api:
    :param user_id:
    :param message:
    :param kwargs:
    :return:
    """
    """
    :param api:
    :param user_id:
    :param message:
    :param kwargs:
    :return:
    """
    data_dict = {
        'user_id': user_id,
        'message': message,
    }
    data_dict.update(**kwargs)
    return api.messages.send(**data_dict)


def get_user_or_group_info(api, nick_or_id):
    if nick_or_id.isalpha() is True:
        nick = nick_or_id + ','
        print(nick)
        res = api.groups.getById(group_ids=nick)
        # res = api.users.get(user_ids = nick)
        # print(res)
        return res[0]['gid']


def get_user_info(api, nick_or_id):
    """
    получение информации о пользователе
    :param api:
    :param nick_or_id:
    :return:
    """
    res = api.users.get(user_ids=nick_or_id, v=api_vk_version)
    return res


def get_audio_id(api, owner_id):
    res = api.audio.get(owner_id=owner_id)
    print(res)


def get_photo_params(api, vk_user_id, photo_id):
    """
    для получения параметров фотографии
    :param api:
    :param vk_user_id:
    :param photo_id:
    :return:
    """
    photos = []
    str_user_id_photo_id = '{}_{}'.format(vk_user_id, photo_id)
    photos.append(str_user_id_photo_id)
    resul = api.photos.getById(photos=photos, extended=1, v=api_vk_version)
    print(resul)
    return resul


# неправильно! надо чтобы был кортеж, а не словарь!
our_users = [
    # {'uid': 18629696, 'can_write_private_message': 1, 'first_name': 'Максим', 'last_name': 'Матюхин'},
    (None, 367999823, 'Каллистратов', 'Иван', 1, None),
    (None, 22252818, 'Гришаева', 'Анна', 1, None)
]

brunko_id = '368514350'
photo_brunko_id = '416510811'
gorkiy_group_id = '-41360940'
volni_veter_uid = 131303037
agr_id = 32007325
gorkiy_id = 18629696

attachments = [
    'audio-41360940_426516897',
    'audio-41360940_327478545',
    'audio-41360940_456239024',
    'audio-41360940_456239025',
    'photo-41360940_378305307'
]

# первая цифра - id владельца, вторая - id аудио
# старые id для Макса
# attachments_for_photo_comment_for_woman = [
#    'audio-41360940_426516897', 'audio-41360940_327478545'
# ]

# накипело: 'audio-41360940_456239019'
# attachments_for_photo_comment_for_man = [
#    'audio-41360940_456239030',  'audio-41360940_426516897'
# ]
# радиус оригинал
# 'audio-58823378_456239067'
# ОСТРОВ!
# 61629833_244602641
# Скотч
# 'audio-61629833_251982666'
# что-то за аудио
# 'audio-61629833_244602641'

# АУДИО ID ДЛЯ ДОБАВЛЕНИЯ ДОЛЖНО БЫТЬ ВЗЯТО ИЗ ГРУППЫ,
# ИМЕННО ИЗ ПЛЕЙЛИСТА ГРУППЫ (НЕ СО СТЕНЫ и ТД)!
# ОСТАЛЬНОЕ ЗАБЛОКИРОВАНО ВК

# Через поля и облака
# attachments_for_photo_comment_for_woman = [
#     'audio-49887978_456239017'
# ]
# attachments_for_photo_comment_for_man = [
#     'audio-49887978_456239017'
# ]

# Сломались отношения
attachments_for_photo_comment_for_woman = [
    'audio-49887978_456239045'
]
attachments_for_photo_comment_for_man = [
    'audio-49887978_456239045'
]
# Нежность звёзд
# attachments_for_photo_comment_for_woman = [
#     'audio-49887978_456239030'
# ]
# attachments_for_photo_comment_for_man = [
#     'audio-49887978_456239030'
# ]

# Контролируй Сердце Солнца
# attachments_for_photo_comment_for_woman = [
#     'audio-49887978_456239019'
# ]
# attachments_for_photo_comment_for_man = [
#     'audio-49887978_456239019'
# ]

# ТОК!
# attachments_for_photo_comment_for_man = [
#     'audio-49887978_456239021'
# ]

# ТОК!
# attachments_for_photo_comment_for_woman = [
#     'audio-49887978_456239021'
# ]

# ИзСебя
# attachments_for_photo_comment_for_man = [
#     'audio-49887978_456239022'
# ]

# ИзСебя
# attachments_for_photo_comment_for_woman = [
#     'audio-49887978_456239022'
# ]

photo_old = ['audio-41360940_456239024', 'audio-41360940_456239025', 'photo-41360940_378305307']


def add_friend(api, user_id):
    return api.friends.add(user_id)


def add_wall_like(api, owner_id, wall_post_id):
    like_res = api.likes.add(type='wall', owner_id=owner_id, item_id=wall_post_id, v=api_vk_version)


def get_wall_posts(api, owner_id=-49887978, **kwargs):
    """
    получает посты, сделанные на стене целевой группы
    :param api:
    :param owner_id:
    :param kwargs:
    :return:
    """
    logger.info("{} - get wall posts".format(owner_id))
    data_dict = {
        'owner_id': owner_id,
    }
    logger.info(data_dict)
    return api.wall.get(v=api_vk_version, **data_dict)


def posts_wall_message(api, owner_id, message, attachments, **kwargs):
    """
    постит единичное сообщение на стенку
    """
    data_dict = {
        'owner_id': owner_id,
        'message': message,
        'attachments': attachments
    }
    data_dict.update(**kwargs)
    return api.wall.post(**data_dict)


def many_posts_wall_message(
        api,
        postgres_con,
        postgres_cur,
        group_id,
        attachments_for_wall_post=attachments,
        message=None,
        is_run_from_interface=False,
        auto_captcha=False,
):
    tupl_members_inner = select_group_users_union_from_inner_db(postgres_con, postgres_cur, group_id)

    for user in tupl_members_inner:
        # если в личку и коммент_авы - False и нет данных об отправке поста на стену, пробуем отправить
        # print(user[5],user[9], user[14])
        if (user[5] is False or user[5] is None) and (user[9] is False) and (user[14] is None):
            # пока используем ф-у make_message_in_privat
            message = make_message_in_privat(user[3], '{}, Горький, очень...!!!')

            data_dict = {
                'owner_id': user[1],
                'message': message,
                'attachments': attachments_for_wall_post
            }
            # data_dict.update(**kwargs)
            try:
                print(user)
                res = api.users.get(user_ids=(user[1],), fields=['can_post'])
                print(res)
                time.sleep(0.3)
                if res[0]['can_post'] == 1:
                    api.wall.post(**data_dict)
                    print('POSTed SUCCESS!')
                    update_to_vk_wall_post_state_group_user_union(postgres_con, postgres_cur, user[0])
                    time.sleep(0.3)

                else:
                    update_to_vk_wall_post_state_group_user_union(
                        postgres_con, postgres_cur, user[0], can_post_wall_comment=False
                    )
            except vk.exceptions.VkAPIError as erro:
                print(erro)
                if erro.message == 'Captcha needed':
                    # если параметр True, то функция становится генератором для приема данных от
                    # интерфейса с помощью send
                    if is_run_from_interface is True:
                        if auto_captcha:
                            save_have_got_captcha(erro)  # сохраняем каптчу в файл
                            captcha_inputed = work_with_RuCaptcha()
                        else:
                            webbrowser.open_new_tab(erro.error_data['captcha_img'])
                            print(erro.error_data['captcha_img'])
                            captcha_inputed = yield 'handling_exception_captcha needed'
                            time.sleep(15)
                            print("DEBUG_2", captcha_inputed)
                        # вторая ветка исключений (обработка) на случай неверно введённой капчи
                        try:
                            api.wall.post(
                                captcha_sid=erro.error_data['captcha_sid'],
                                captcha_key=captcha_inputed,
                                **data_dict
                            )
                            print('WALL POSTed SUCCESS!')
                            update_to_vk_wall_post_state_group_user_union(postgres_con, postgres_cur, user[0])
                            time.sleep(0.3)
                        except:
                            if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
                                print("Неверно ввели каптчу")

                    else:
                        captcha_inputed = input()
                        # вторая ветка исключений (обработка) на случай неверно введённой капчи
                        try:
                            res = api.wall.post(
                                captcha_sid=erro.error_data['captcha_sid'],
                                captcha_key=captcha_inputed,
                                **data_dict
                            )
                            print('POSTed SUCCESS!')
                            update_to_vk_wall_post_state_group_user_union(postgres_con, postgres_cur, user[0])
                            time.sleep(0.3)
                        except:
                            if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
                                print("Неверно ввели каптчу")

                elif erro.message == 'Access to adding post denied: too many messages sent':
                    print('Достигнут лимит постов на стенку. Завершаем функцию')
                    return 'OK'
                elif erro.message == 'Too many recipients':
                    print('Возникла ошибка "слишком много получателей. Вероятно, нужно изменить текст')
                    return 'OK'
            # todo доделать функцию!!!!
    return


def deco_add_to_friends_with_message(func):
    def wrapper(*args):
        try:
            func(*args)
        except vk.exceptions.VkAPIError as erro:

            if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
                webbrowser.open_new_tab(erro.error_data['captcha_img'])
                print(erro.error_data['captcha_img'])
                captcha_inputed = input()
                captcha_sid = erro.error_data['captcha_sid']
                captcha_key = captcha_inputed
                api = args[0]
                res = api.friends.add(user_id=user_info[1], text=message)
                print('Posted SUCCESSfully!')
                print(res)

                # update_to_vk_photo_comment_state_group_user_union(postgres_con, postgres_cur, user[1])
                # пилять!!!
                # count += 1
                time.sleep(2)

    return wrapper


# @deco_add_to_friends_with_message
def add_to_friends_with_message(
        api, postgres_con, postgres_cur, vk_group_id, message='', attachments=None, captcha_sid=None, captcha_key=None,
        **kwargs
):
    tupl_members_inner = select_users_info(postgres_con, postgres_cur, vk_group_id)
    print(tupl_members_inner)
    count = 0
    for user_info in tupl_members_inner:
        print(user_info[4])

        try:
            if user_info[4] == 0 and user_info[9] is False and user_info[8] == -1 and user_info[13] is None:
                print(user_info)
                # ставим лайк!!!
                # try:
                # like_res = api.likes.add(type='photo', owner_id= user_info[1], item_id=user_info[8])
                # это типа псевдодекоратор
                # print(like_res, 'done like')
                # except vk.exceptions.VkAPIError as erro:
                # print('перехватили исключение при попытке лайкнуть. Здесь ничего не делаем пока')
                # print(erro)
                # todo реализовать логику обработки исключения
                # добавляем юзера в друзья
                res = api.friends.add(user_id=user_info[1], text=message)
                print(res)
                if res == 1:
                    update_to_vk_group_user_friend_added(postgres_con, postgres_cur, user_info[0])
                else:
                    print('warning! cant add friend')

        except vk.exceptions.VkAPIError as erro:

            if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
                webbrowser.open_new_tab(erro.error_data['captcha_img'])
                print(erro.error_data['captcha_img'])
                captcha_inputed = input()
                captcha_sid = erro.error_data['captcha_sid']

                res = api.friends.add(
                    user_id=user_info[1], text=message, captcha_sid=captcha_sid, captcha_key=captcha_inputed
                )
                update_to_vk_group_user_friend_added(postgres_con, postgres_cur, user_info[0])
                print('added friend SUCCESSfully after inputing captcha!')
                print(res)
                # update_to_vk_photo_comment_state_group_user_union(postgres_con, postgres_cur, user[1]) # пилять!!!
                count += 1


def add_bots_to_friends_of_each_other(postgres_con, postgres_cur, users_api, bots_senders):
    """
    Добавляет ботов во взаимные друзья
    :param postgres_con: не нужно! к удалению
    :param postgres_cur:
    :param users_api:
    :param bots_senders:
    :return:
    """
    for bots_api_num in range(len(users_api)):
        print('{}: добавляем в друзья к {}'.format(datetime.now(), users_api[bots_api_num][3]))
        for bots_num2 in range(1, len(bots_senders)):
            try:
                res = users_api[bots_api_num][0].friends.add(
                    user_id=bots_senders[bots_num2].vk_user_id,
                    text='добавляем в друзья',
                    v=api_vk_version
                )
                print(res)
                if res == 1:
                    print('{}: пользователь {} успешно добалвен в друзья к {}'.format(
                        datetime.now(),
                        bots_senders[bots_num2],
                        bots_api_num
                    ))
                    # time.sleep(1)
                else:
                    print('warning! cant add friend, may be He is already friend?')
            except vk.exceptions.VkAPIError as erro:
                print(erro)
                if erro.message == 'Captcha needed':
                    # если параметр True,
                    # то функция становится генератором для приема данных от интерфейса с помощью send
                    save_have_got_captcha(erro)  # сохраняем каптчу в файл
                    captcha_guessed = work_with_RuCaptcha()
                    captcha_sid = erro.error_data['captcha_sid'],
                    res = users_api[bots_api_num][0].friends.add(
                        user_id=bots_senders[bots_num2].vk_user_id,
                        text='добавляем в друзья',
                        captcha_sid=captcha_sid,
                        captcha_key=captcha_guessed
                    )
                    print(res)
                    if res == 1:
                        print('{}: пользователь {} успешно добалвен в друзья к {}'.format(
                            datetime.now(),
                            bots_senders[bots_num2],
                            bots_api_num
                        ))
                    else:
                        print('warning! cant add friend')
            time.sleep(3)


def deco_create_photo_comment(create_photo_comment):
    def wrapper(*args):
        try:
            create_photo_comment(*args)
        except vk.exceptions.VkAPIError as erro:
            if erro.code == 7:  # error_data - это словарь, где хранятся данные о вернувшейся ошибке api
                print('access closed')
                print(erro.message)
                if erro.message == 'Permission to perform this action is denied: photo is deleted':
                    print(erro, 'обновляем инфо о фото в БД')
                    update_to_vk_photo_comment_state_group_user_union(postgres_con, postgres_cur, user[1],
                                                                      can_post_ava_comment=False)

    return wrapper


def create_photo_comment(
        api, owner_id, photo_id, message, attachments=None, captcha_sid=None, captcha_key=None, **kwargs
):
    """
    постинг комментария к фото
    :param api:
    :param owner_id:
    :param photo_id:
    :param message:
    :param attachments:
    :param captcha_sid:
    :param captcha_key:
    :param kwargs:
    :return:
    """
    if captcha_sid is None and captcha_key is None:
        api.photos.createComment(
            v=api_vk_version, owner_id=owner_id, photo_id=photo_id, message=message, attachments=attachments
        )
    else:
        api.photos.createComment(
            v=api_vk_version, owner_id=owner_id, photo_id=photo_id, message=message, attachments=attachments,
            captcha_sid=captcha_sid, captcha_key=captcha_key)

def make_message_in_privat(user_name, user_text=None, is_multitext=False):
    # todo странная логика у функции. Подумать!!
    """
    :type user_text: object
    """
    if user_text is None:
        user_text = "Добрый день, {}! Сорри за спам :// Но будет классно, " \
                    "если Вы послушаете и оцените немного нашей музыки) ".format(user_name)
    elif is_multitext:
        random_text_index = random.randint(1, user_text.count())
        user_text = user_text.get(id=random_text_index).ava_message.format(user_name)
        print('Текст для отправки: ', user_text)
        logger.info('Текст для отправки: {}'.format(user_text))
    elif user_text.find('{}') != -1:
        user_text = user_text.format(user_name)

    return user_text


def handling_captcha_exeption(erro):
    """
    обработка исключения, возникающего при необходимости ввода капчи
    :param erro:
    :return:
    """
    if erro.error_data['error_code'] == 7:  # error_data - это словарь, где хранятся данные о вернувшейся ошибке api
        print('access closed')
        time.sleep(2)
    elif erro.error_data['error_code'] == 14:
        print(dir(erro))
        print(erro.message)
        print(erro.error_data)
        print(erro.is_captcha_needed())
        if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
            webbrowser.open_new_tab(erro.error_data['captcha_img'])
            print(erro.error_data['captcha_img'])
            captcha_inputed = input()
            # res = fun()
            return captcha_inputed


def final_sending_privat_message(api, conn, cur, vk_group_id, offset=0, count_of_end_work=10):
    """
    главная функция для отправки сообщений в личку
    оффсет должен быть ассоциирован с count !!! иначе капут
    :return:
    """
    postgres_con, postgres_cur = connection_to_postgres()
    # tupl_members_inner =  select_group_users_from_inner_db(postgres_con, postgres_cur)# our_users #
    # здесь мы используем версию функции для запроса с ЛОКЕРОМ (for update)
    # our_users in group #
    tupl_members_inner = select_group_users_union_from_inner_db_FOR_UPDATE(postgres_con, postgres_cur, vk_group_id)
    texts_list = [
        'Здравствуйте, {}! Послушайте музыку молодой т перспективной группы)  \
         ЕСЛИ ВАМ НЕ ИНТЕРЕСНО, ПРОСТО ПРОИГНОРИРУЙТЕ СООБЩЕНИЕ!',
        'День добрый, {}! Не судите строго молодую группу :/ ',
        'Добрый день, {}! Просьба понять, простить за спам и оценить нашу музыку) ',
        'Здравствуйте, {}! Не судите строго молодых музыкантов :// '
        'Пожалуйста, не жалуйтесь на мое сообщение, мы хорошие)',
        'День добрый, {}! У нас тут альбом вышел... Будем рады, если оцение :/   Будем очень рады!!',
        'Здравствуйте, {}! Послушайте музыку молодой т перспективной группы)   СПАСИБО ЗАРАНЕЕ',
        'День добрый, {}! У нас тут альбом вышел... Будем рады, если оцение :/ ',
    ]
    count = 0
    for user in tupl_members_inner[offset:]:
        # метод для отсылки сообщений!!
        # print(user)
        if user[4] == 1 and user[6] is not True:
            # print(user)
            # вызываем вспомогательную функцию, формирующую текстЫ сообщениЙ
            message = make_message_in_privat(user[3], texts_list[count])
            # todo параметризировать attachments в функции
            try:
                # вызываем вспомогательную функцию для фактической отсылки сообщений
                res = send_message(api, user_id=user[1], message=message, attachment=attachments)
                print(res)
                # обновляем запись в БД (ставим признак True для отосланных сообщений
                update_to_vk_group_user_union(postgres_con, postgres_cur, user[1])
                count += 1
                time.sleep(5)
            except vk.exceptions.VkAPIError as erro:
                if erro.message == 'Permission to perform this action is denied.':
                    # обновляем запись в БД (ставим признак True для отосланных сообщений
                    update_to_vk_group_user_union(postgres_con, postgres_cur, user[1], didnt_send=True)
            if count == count_of_end_work:
                return 'OK'
            # print (res2)


def final_sending_privat_message_with_multisender(
        api, conn, cur, vk_group_id, text_list_for_multitext, count_of_end_work=2
):
    """
    главная функция для отправки сообщений в личку
    оффсет должен быть ассоциирован с count !!! иначе капут
    :return:
    """
    postgres_con, postgres_cur = connection_to_postgres()
    # tupl_members_inner =  select_group_users_from_inner_db(postgres_con, postgres_cur)# our_users #
    # здесь мы используем версию функции для запроса с ЛОКЕРОМ (for update)
    # our_users in group#
    tupl_members_inner = select_group_users_union_from_inner_db_FOR_UPDATE(postgres_con, postgres_cur, vk_group_id)
    max_index = len(text_list_for_multitext)
    offset = 0
    count = 0
    for user in tupl_members_inner:
        # метод для отсылки сообщений!!
        # print(user)
        if user[4] == 1 and user[6] is not True:
            if offset == max_index: offset = 0
            print("send message to user: ", user)
            # вызываем вспомогательную функцию, формирующую текстЫ сообщениЙ
            message = make_message_in_privat(user[3], text_list_for_multitext[offset])
            # todo параметризировать attachments в функции
            try:
                # вызываем вспомогательную функцию для фактической отсылки сообщений
                res = send_message(api, user_id=user[1], message=message, attachment=attachments)
                print(res)
                # обновляем запись в БД (ставим признак True для отосланных сообщений
                update_to_vk_group_user_union(postgres_con, postgres_cur, user[1])
                offset += 1
                count += 1
                time.sleep(5)
            except vk.exceptions.VkAPIError as erro:
                if erro.message == 'Permission to perform this action is denied.':
                    # обновляем запись в БД (ставим признак True для отосланных сообщений
                    update_to_vk_group_user_union(postgres_con, postgres_cur, user[1], didnt_send=True)
            if count == count_of_end_work:
                return 'OK'


def final_getting_subscribers(api, group_id, offset=0, insert_to_aim_group=False):
    """
    метод для получения подписчиков сообщества записи результатов в БД
    если задан параметр insert_to_aim_group, производится работа с таблицей для целевой группы (которую пиарим)
    offset: показывает смещение стартовой позиции для выгрузки относительно нулевого пользователя
    """
    dict_res_members_of_group = api.groups.getMembers(
        group_id=group_id,
        fields=['can_write_private_message', 'sex', 'bdate', 'city'],
        offset=offset,
        v=api_vk_version
    )
    # print(dict_res_members_of_group)

    postgres_con, postgres_cur = connection_to_postgres()

    # tupl_member_of_group = make_tuple_for_insert_record_to_vk_group_user(dict_res_members_of_group)
    # формирование строки инсерта
    # в предыдущих версиях vk api ключ с пользователями был 'users'
    tupl_member_of_group = tuple(dict_res_members_of_group['items'])
    if insert_to_aim_group:
        insert_res = make_insert_records_to_aim_group(postgres_con, postgres_cur, tupl_member_of_group)
    else:
        insert_res = make_insert_records_to_vk_group_user_union(
            postgres_con, postgres_cur, tupl_member_of_group, group_id
        )
    return insert_res


def final_getting_subscribers_with_offsets_loop(api, group_id, end_digit=None, offset=1000, insert_to_aim_group=False):
    """
    функция, которая бежит по оффсетам для получения ВСЕХ подписчиков группы.
    нужна, потому что за раз можно дернуть только 1000 пользователей
    """
    # сначала нужно узнать, сколько подписчиков в группе
    group_info = api.groups.getById(group_id=group_id, fields=['members_count'], v=api_vk_version)
    count_of_subscribers = group_info[0]['members_count']
    end_digit = count_of_subscribers + 1000
    if insert_to_aim_group:
        for inner_offset in range(0, end_digit, offset):
            res = final_getting_subscribers(api, group_id, offset=inner_offset, insert_to_aim_group=insert_to_aim_group)
            time.sleep(0.5)
            print(res)
    else:
        for inner_offset in range(0, end_digit, offset):
            res = final_getting_subscribers(api, group_id, offset=inner_offset)
            time.sleep(0.5)
            print(res)
    print('done')

    return 'ОК'


def get_ava_id_and_insert_in_into_db(
        api,
        postgres_con,
        postgres_cur,
        group_id=None,
        min_value=None,
        offset=None,
        delay_between_gets=0.4,
        list_users_info=None
):
    """
    метод для выдергивания id аватарок и записи их в БД
    min_value и offset может быть удалён в следующей версии
    """
    print(postgres_cur, postgres_con)
    # time.sleep(20)
    if not postgres_con and not postgres_cur:
        print('получаем подключение к БД')
        postgres_con, postgres_cur = connection_to_postgres()
    if not list_users_info:
        print('список пользователей не передан')
        list_users_info = select_users_info(postgres_con, postgres_cur, group_id, min_value, offset)
    else:
        print('список пользователей передан')
        pass
    for user_info in list_users_info:
        print(user_info)

    for user_info in list_users_info:
        print(user_info)
        if user_info[8] is None:
            print(user_info[1])
            try:
                res = api.users.get(user_ids=user_info[1], fields=['photo_id'], v=api_vk_version)
                print(res)
                if 'photo_id' in res[0].keys():
                    photo_id = res[0]['photo_id'].split('_')[1]
                    print(photo_id)
                    update_to_vk_group_user_union_ava_id(postgres_con, postgres_cur, photo_id, user_info[1])
                else:
                    # если идентификатора фото нет, проставляем False в возможности комментить
                    update_to_vk_group_user_union_can_comment_ava(postgres_con, postgres_cur, user_info[8],
                                                                  user_info[1], False)
                    print('cant_comment_ava')
                time.sleep(delay_between_gets)
            except requests.exceptions.ReadTimeout:
                print('не удалось выполнить http-запрос, пробуем снова')
    return 'OK'


def get_settings_of_photo(
        api,
        postgres_con,
        postgres_cur,
        group_id=None,
        is_run_from_interface=None,
        delay_between_gets=0.4,
        list_users_info=None
):
    """
    метод для выдергивания настроек приватности для аватарок
    """
    print("запущено из интерфейса? {}".format(is_run_from_interface))
    if postgres_con and postgres_cur is None:
        postgres_con, postgres_cur = connection_to_postgres()
    if not list_users_info:
        print('список пользователей для получения настроек аватарок не передан')
        list_users_info = select_users_info(postgres_con, postgres_cur, group_id)
    else:
        print('список для получения настроек аватарок пользователей передан')
        pass
    for user_info in list_users_info:
        print("{}: получаем настройки авы для {}".format(datetime.now(), user_info))
        # todo не сюда!
        try:
            if user_info[8] is not None and user_info[8] != -1 and user_info[9] is None:
                # time.sleep(30)
                try:
                    res = get_photo_params(api, user_info[1], user_info[8])
                    time.sleep(delay_between_gets)
                    if res[0]['can_comment'] == 1:
                        update_to_vk_group_user_union_can_comment_ava(postgres_con, postgres_cur, user_info[8],
                                                                      user_info[1], True)
                    else:
                        update_to_vk_group_user_union_can_comment_ava(postgres_con, postgres_cur, user_info[8],
                                                                      user_info[1], False)
                        print('фото комментить нельзя')
                except vk.exceptions.VkAPIError as erro:
                    if erro == 'Access Denied':
                        print('исключение при попытке получить настройки фотографии')
                        update_to_vk_group_user_union_can_comment_ava(postgres_con, postgres_cur, user_info[8],
                                                                      user_info[1], False)
        except requests.ReadTimeout:
            print('не удалось выполнить http-запрос, пробуем снова')
            time.sleep(60)


def select_min_max_uncaptured_photo_ids_gr_user_union(postgres_con, postgres_cur, group_id):
    """
    ВЫборка мин и макс ID ищ необработанных пользователей группы
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :return:
    """
    query_for_min = '''
            SELECT min(id) FROM vk_group_user_union_2
            WHERE vk_group_id = '{}' and avatar_id IS NULL
        '''.format(group_id)

    query_for_max = '''
            SELECT max(id) FROM vk_group_user_union_2
            WHERE vk_group_id = '{}' and avatar_id IS NULL
        '''.format(group_id)
    try:
        print(query_for_min)
        response = postgres_cur.execute(query_for_min)
        min_id = postgres_cur.fetchall()[0][0]
        print(response)
        response = postgres_cur.execute(query_for_max)
        print(response)
        max_id = postgres_cur.fetchall()[0][0]
        print(min_id, max_id)
        return min_id, max_id
    except psycopg2.IntegrityError:
        print('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))
        logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def select_min_max_uncaptured_ava_params_gr_user_union(postgres_con, postgres_cur, group_id):
    """
    ВЫборка мин и макс ID ищ необработанных пользователей группы
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :return:
    """
    query_for_min = '''
            SELECT min(id) FROM vk_group_user_union_2
            WHERE vk_group_id = '{}' and avatar_id IS NOT NULL
            AND can_post_ava_comment != false
        '''.format(group_id)

    query_for_max = '''
            SELECT max(id) FROM vk_group_user_union_2
            WHERE vk_group_id = '{}' and avatar_id IS NOT NULL
            AND can_post_ava_comment != false
        '''.format(group_id)
    try:
        print(query_for_min)
        response = postgres_cur.execute(query_for_min)
        min_id = postgres_cur.fetchall()[0][0]
        print(response)
        response = postgres_cur.execute(query_for_max)
        max_id = postgres_cur.fetchall()[0][0]
        print(min_id, max_id)
        return min_id, max_id
    except psycopg2.IntegrityError:
        print('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))
        logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def select_gr_users_for_multiproc_getting_ava_params(
        postgres_con, postgres_cur, group_id, min_id, max_id
):
    query = '''
              SELECT * FROM vk_group_user_union_2
                  WHERE
                      vk_group_id='{}'
                      AND avatar_id IS NOT NULL
                      AND can_post_ava_comment != false
                      AND id>='{}'
                      AND id<'{}'
          '''.format(group_id, min_id, max_id)
    print(query)
    try:
        postgres_cur.execute(query)
        result = postgres_cur.fetchall()
        # print(result)
        # time.sleep(5)
        # print(result)
        if postgres_cur.statusmessage != 0:
            return result  # str(postgres_cur.statusmessage)
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def select_gr_users_for_multiproc_getting_photo_ids(
        postgres_con,
        postgres_cur,
        group_id,
        min_id,
        max_id
):
    query = '''
              SELECT * FROM vk_group_user_union_2
                  WHERE
                      vk_group_id='{}'
                      AND avatar_id IS NULL
                      AND id>='{}'
                      AND id<'{}'
          '''.format(group_id, min_id, max_id)
    print(query)
    try:
        postgres_cur.execute(query)
        result = postgres_cur.fetchall()
        # print(result)
        # time.sleep(5)
        # print(result)
        if postgres_cur.statusmessage != 0:
            return result  # str(postgres_cur.statusmessage)
    except psycopg2.IntegrityError:
        logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def multiproc_get_photo_params(
        users_apis,
        group_id,
        is_run_from_interface=True,
        delay_between_posts=0.4
):
    """
    #todo подумать над ДЕКОРАТОРОМ?
    :param users_apis:
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :param consider_user_sex:
    :param is_run_from_interface:
    :param delay_between_posts:
    :param auto_captcha:
    :param is_multitext:
    :param limit_count_of_message:
    :return:
    """
    print("Запущено из интерфейса? {}".format(is_run_from_interface))
    count_of_needed_process = len(users_apis)
    postgres_con, postgres_cur = connection_to_postgres()
    lis_of_users = []
    all_process = []
    min_id, max_id = select_min_max_uncaptured_photo_ids_gr_user_union(postgres_con, postgres_cur, group_id)
    offset = (max_id - min_id) // count_of_needed_process
    print('смещение для генераторов: ', offset)
    '''
    def gen_starter(*args):
        #print(*args[0], *args[1], *args[2], *args[3])
        #time.sleep(30)
        con, cur = connection_to_postgres()
        args = list(args)
        args[1] = con
        args[2] = cur
        args = tuple(args)

        gen = do_comment_photo(*args)
        for item in gen:
            print(item)
            logger_for_communicator.info('user: {}'. format(item))'''

    while min_id < max_id:
        temporary_max = min_id + offset
        lis_of_users.append(
            # todo тут исправить запрос??? надо ли?
            select_gr_users_for_multiproc_getting_photo_ids(
                postgres_con,
                postgres_cur,
                group_id,
                min_id,
                temporary_max)
        )
        min_id += offset
    # return lis_of_users
    print(lis_of_users)
    gens_list = []
    '''
    for ind in range(0, count_of_needed_process):
        print(lis_of_users[ind])
        gens_list.append(gen_starter(
            users_apis[ind],
            postgres_con,
            postgres_cur,
            group_id,
            consider_user_sex,
            is_run_from_interface,
            delay_between_posts,
            auto_captcha,
            is_multitext ,
            limit_count_of_message,
            bot_sender,
            lis_of_users[ind][0]
            )
        )'''
    # в данном движке psycopg2 для разных процессов нужно создавать
    # разные подключения. В противном случае, возвращается ошибка
    # psycopg2.OperationalError: SSL SYSCALL error: EOF detected
    # ошибка не из-за этого, однако, все равно предпочтительно создавать разные подключения.
    # ошибка из за наличия подключения "внутри Джанго" (основное подключение для приложения
    # пока решил, согласно совету StackOverFlow импортированием подключений Джанго
    # и принудительным их отключением
    # тесты показывают, что, предположительно, подключение поднимается заново при необходимости
    # при обращении их интерфейса
    # (нуждается в доп. тестах!)webdriver.Chrome('/home/grishaev/PycharmProjects/VKSpammer/WebDriver/chromedriver')

    db.connections.close_all()
    for ind in range(0, count_of_needed_process):
        # lis_ind_postgres_con, lis_ind_postgres_cur = multiconnection_to_postgres(count_of_needed_process)
        # print(ind_postgres_cur)
        # print(lis_ind_postgres_cur)
        p = Process(target=get_ava_id_and_insert_in_into_db, args=(
            users_apis[ind][0],
            # тут долбань с объектами подключений во внут БД
            None,
            None,
            group_id,
            None,
            None,
            delay_between_posts,
            lis_of_users[ind]
        )
                    )
        print('создали процесс!')
        all_process.append(p)
    for p in all_process:
        p.start()
        print('запустили процесс!')
        time.sleep(3)


def get_subscriber_settings_with_multisender_and_multiproc(api, postgres_con, postgres_cur, group_id, min_value,
                                                           offset):
    result = get_ava_id_and_insert_in_into_db(api, postgres_con, postgres_cur, group_id, min_value, offset)
    if result == 'OK':
        return result
    else:
        raise ValueError


def decorator_do_comment_photo(do_comment_photo):
    def wrapper_do_comment_photo(api, postgres_con, postgres_cur, vk_group_id, consider_user_sex,
                                 is_run_from_interface):
        if is_run_from_interface is True:
            generator_for_commenting = do_comment_photo(
                api, postgres_con, postgres_cur, vk_group_id, consider_user_sex, is_run_from_interface
            )
            gen_result = next(generator_for_commenting)
            x = True
            while x is True:
                try:
                    if gen_result == 'handling_exception':
                        # todo всплывающее окно
                        # window_for_captcha(request)
                        generator_file = open('generator_file', 'w')
                        # temp = pickle.dumps(generator_for_commenting)
                        generator_file.close()
                        x = False
                        # inputed_captcha = input()
                        # generator_for_commenting.send(inputed_captcha)
                    gen_result = next(generator_for_commenting)
                except StopIteration:
                    x = False

        elif is_run_from_interface is False:
            do_comment_photo(
                api, postgres_con, postgres_cur, vk_group_id, consider_user_sex
            )

    return wrapper_do_comment_photo


def save_have_got_captcha(erro):
    captcha_have_got = requests.get(erro.error_data['captcha_img'])
    captcha_saved_image = Image.open(BytesIO(captcha_have_got.content))
    # print(captcha_have_got.content)
    # captcha_file = open("captcha_file.jpg","wb") # для сохранения файла
    captcha_saved_image.save("captcha_file.jpg")
    # time.sleep(400)


def multiproc_do_comment_photo(
        users_apis,
        postgres_con,
        postgres_cur,
        group_id,
        consider_user_sex=False,
        is_run_from_interface=True,
        delay_between_posts=4,
        auto_captcha=False,
        is_multitext=False,
        limit_count_of_message=90,
        bot_sender=None
):
    """
    #todo подумать над ДЕКОРАТОРОМ?
    :param users_apis:
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :param consider_user_sex:
    :param is_run_from_interface:
    :param delay_between_posts:
    :param auto_captcha:
    :param is_multitext:
    :param limit_count_of_message:
    :param bot_sender:
    :return:
    """
    count_of_needed_process = len(users_apis)

    lis_of_users = []
    allProcess = []
    min_id, max_id = select_min_max_unhandled_id_gr_user_union(postgres_con, postgres_cur, group_id)
    offset = (max_id - min_id) // count_of_needed_process
    print('смещение для генераторов: ', offset)

    def gen_starter(*args):
        # print(*args[0], *args[1], *args[2], *args[3])
        # time.sleep(30)
        con, cur = connection_to_postgres()
        args = list(args)
        args[1] = con
        args[2] = cur
        args = tuple(args)

        gen = do_comment_photo(*args)
        for item in gen:
            print(item)
            logger.info('user: {}'.format(item))
        con.close()
        print("{}: работа генератора завершена, удалось закрыть подключение к БД".format(datetime.now()))

    while min_id < max_id:
        temporary_max = min_id + offset
        lis_of_users.append(
            select_gr_users_union_from_inner_db_for_multiproc(
                postgres_con,
                postgres_cur,
                group_id,
                min_id,
                temporary_max)
        )
        min_id += offset
    # return lis_of_users
    # print(lis_of_users)
    gens_list = []
    '''
    for ind in range(0, count_of_needed_process):
        print(lis_of_users[ind])
        gens_list.append(gen_starter(
            users_apis[ind],
            postgres_con,
            postgres_cur,
            group_id,
            consider_user_sex,
            is_run_from_interface,
            delay_between_posts,
            auto_captcha,
            is_multitext ,
            limit_count_of_message,
            bot_sender,
            lis_of_users[ind][0]
            )
        )'''
    # в данном движке psycopg2 для разных процессов нужно создавать
    # разные подключения. В противном случае, возвращается ошибка
    # psycopg2.OperationalError: SSL SYSCALL error: EOF detected
    # ошибка не из-за этого, однако, все равно предпочтительно создавать разные подключения.
    # ошибка из за наличия подключения "внутри Джанго" (основное подключение для приложения
    # пока решил, согласно совету StackOverFlow импортированием подключений Джанго
    # и принудительным их отключением
    # тесты показывают, что предположительно подключение поднимается заново при необходимости
    # при обращении их интерфейса (нуждается в доп. тестах!)
    # webdriver.Chrome('/home/agrishaev/PycharmProjects/VKSpammer/WebDriver/chromedriver')

    db.connections.close_all()
    for ind in range(0, count_of_needed_process):
        # lis_ind_postgres_con, lis_ind_postgres_cur = multiconnection_to_postgres(count_of_needed_process)
        # print(ind_postgres_cur)
        # print(lis_ind_postgres_cur)
        p = Process(target=gen_starter, args=(
            users_apis[ind][0],
            # тут долбань с объектами подключений во внут БД
            None,
            None,
            group_id,
            consider_user_sex,
            is_run_from_interface,
            delay_between_posts,
            auto_captcha,
            is_multitext,
            limit_count_of_message,
            bot_sender,
            lis_of_users[ind]
        )
                    )
        allProcess.append(p)
    # for gen in gens_list:
    #    p = Process(target=gen_starter, args=gen)
    #    allProcess.append(p)
    # print(allProcess)

    for p in allProcess:
        p.start()
        print('запустили процесс!')
        time.sleep(3)


# @decorator_do_comment_photo
def do_comment_photo(
        api,
        postgres_con,
        postgres_cur,
        group_id,
        consider_user_sex=False,
        is_run_from_interface=False,
        delay_between_posts=3,
        auto_captcha=False,
        is_multitext=False,
        limit_count_of_message=90,
        bot_sender=None,
        list_of_vk_users_to_send=None
):
    """
    комментирование аватарок
    :param api:
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :param consider_user_sex:
    :param is_run_from_interface:
    :param delay_between_posts:
    :param auto_captcha:
    :param is_multitext:
    :param limit_count_of_message:
    :param bot_sender:
    :param list_of_vk_users_to_send:
    :return:
    """
    if is_multitext:
        # если параметр is_multitext передается, то тексты передаются в нём!!
        message_text = is_multitext
    else:
        message_text = '{}, С новым годом!)))'
    list_of_vk_errors = select_vk_errors(postgres_con, postgres_cur)
    print('список ошибок:', list_of_vk_errors)

    # костыль для отправки посредством мультипроцессинга, но что поделать!!
    # костыль для отправки посредством мультипроцессинга, но что поделать!!
    if list_of_vk_users_to_send is None:
        tupl_members_inner = select_group_users_union_from_inner_db(postgres_con, postgres_cur, group_id)
    else:
        tupl_members_inner = list_of_vk_users_to_send

    # print('Got users to sending ava comment: ', tupl_members_inner)
    count = 0
    for user in tupl_members_inner:
        # метод для комментирования фоток
        # print(user)
        if bot_sender:
            if bot_sender.day_sent_message_count > limit_count_of_message:
                print("Messages limit for sender reached, distribution is finished", bot_sender)
                break
                # todo ну капец ущербная логика. сделал так только из-за отсутствия времени
        if count > limit_count_of_message:
            # здесь прерываем цикл. В случае генератора, возбуждается исключение StopIteration
            break

        if user[9] is True and user[5] is not True and user[6] is not True:
            print(user)
            # ставим лайк!!!
            try:
                try:
                    like_res = api.likes.add(type='photo', owner_id=user[1], item_id=user[8],
                                             v=api_vk_version)  # псевдодекоратор
                    print(like_res, 'done like')
                    logger.info('done_like: {}'.format(like_res))
                except vk.exceptions.VkAPIError as erro:
                    logging.warning("Исключение при попытке лайкнуть", erro)
                    if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
                        print('перехватили исключение при попытке лайкнуть.')
                        save_have_got_captcha(erro)  # сохраняем каптчу в файл
                        captcha_guessed = work_with_RuCaptcha()
                        # webbrowser.open_new_tab(erro.error_data['captcha_img']) # открываем фото с капчей.
                        print(erro.error_data['captcha_img'])
                        # если параметр True, то функция становится генератором для приема данных
                        # от интерфейса с помощью send
                        if is_run_from_interface is True:
                            captcha_inputed = yield 'handling_exception'
                            print("DEBUG", captcha_inputed)
                        else:
                            captcha_inputed = input()
                            # ветка обработки исключений на случай ошибки в капче
                        try:
                            like_res = api.likes.add(
                                type='photo',
                                owner_id=user[1],
                                item_id=user[8],
                                captcha_sid=erro.error_data['captcha_sid'],
                                # captcha_key=captcha_inputed
                                captcha_key=captcha_guessed,
                                v=api_vk_version
                            )
                            print(like_res, 'done like after captcha input')
                        except vk.exceptions.VkAPIError as erro:
                            if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
                                print("Неверно ввели каптчу")
                time.sleep(delay_between_posts)
            except TimeoutError:
                print('отловили ошибку Http-таймаута')
                pass
                # todo как-то обработать исключение?
            # делаем пост под фото!!!
            try:  # перехватываем исключения капчи и недостатка прав
                if consider_user_sex is True:
                    if user[10] == '1':
                        # вызываем вспомогательную функцию формирования текста
                        message = make_message_in_privat(user[3], message_text, is_multitext)
                        create_photo_comment(
                            api,
                            owner_id=user[1],
                            photo_id=user[8],
                            message=message,
                            attachments=attachments_for_photo_comment_for_woman
                        )

                    elif user[10] == '2':
                        # вызываем вспомогательную функцию формирования текста
                        message = make_message_in_privat(user[3], message_text, is_multitext)
                        create_photo_comment(
                            api,
                            owner_id=user[1],
                            photo_id=user[8],
                            message=message,
                            attachments=attachments_for_photo_comment_for_man
                        )
                else:
                    # вызываем вспомогательную функцию формирования текста
                    message = make_message_in_privat(user[3], message_text, is_multitext)
                    create_photo_comment(
                        api,
                        owner_id=user[1],
                        photo_id=user[8],
                        message=message,
                        attachments=attachments_for_photo_comment_for_woman
                    )

                update_to_vk_photo_comment_state_group_user_union(postgres_con, postgres_cur, user[1])  # пилять!!!
                print('POSTed SUCCESS!')
                count += 1
                if bot_sender:
                    bot_sender.day_sent_message_count += 1
                    bot_sender.save()

            except vk.exceptions.VkAPIError as erro:
                logging.info(erro)
                print(erro)
                print(erro.message)
                # ветка обработки исключений на случай ошибочной капчи
                if erro.code == 7:  # error_data - это словарь, где хранятся данные о вернувшейся ошибке api
                    print('access closed')
                    if erro.message == 'Permission to perform this action is denied: photo is deleted':
                        print(erro, 'обновляем инфо о фото в БД')
                        update_to_vk_photo_comment_state_group_user_union(
                            postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
                        # todo делать запись в БД!!!!
                    elif erro.message == 'Permission to perform this action is denied: user is not allowed to comment':
                        print(erro, 'обновляем инфо о фото в БД')
                        update_to_vk_photo_comment_state_group_user_union(
                            postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
                    elif erro.message == 'Permission to perform this action is denied: photo access denied':
                        # todo проверить и если ДА - переписать на работу по ID(первичному ключу)
                        print(erro, 'updating photo info in database')
                        update_to_vk_photo_comment_state_group_user_union(
                            postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
                    elif erro.message == 'Permission to perform this action is denied: wall or photo comment not added':
                        print(erro, 'updating photo info in database')
                        update_to_vk_photo_comment_state_group_user_union(
                            postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
                    else:
                        print("Нужно авторизоваться под другим пользователем. Работа скрипта будет завершена")
                        time.sleep(600)
                        time.sleep(delay_between_posts)
                        # todo подумать над доработкой&&&
                        break
                elif erro.error_data['error_code'] == 15:
                    print('Updating photo info in database for vk_user_id: ', erro.request_params['owner_id'])
                    update_to_vk_photo_comment_state_group_user_union(
                        postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
                elif erro.error_data['error_code'] == 14:
                    print(dir(erro))
                    print(erro.message)
                    print(erro.error_data)
                    print(erro.is_captcha_needed())
                    if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
                        save_have_got_captcha(erro)
                        captcha_guessed = work_with_RuCaptcha()
                        # webbrowser.open_new_tab(erro.error_data['captcha_img'])
                        print(erro.error_data['captcha_img'])
                        # если параметр True, то функция становится генератором для приема данных
                        # от интерфейса с помощью send
                        if is_run_from_interface is True:
                            captcha_inputed = yield 'handling_exception'
                            # print("DEBUG_2", captcha_inputed)
                            print("DEBUG_2", captcha_guessed)
                        else:
                            captcha_inputed = input()
                        # вторая ветка исключений (обработка) на случай неверно введённой капчи
                        try:
                            create_photo_comment(
                                api, owner_id=user[1], photo_id=user[8], message=message,
                                attachments=attachments_for_photo_comment_for_woman,
                                captcha_sid=erro.error_data['captcha_sid'],
                                # captcha_key=captcha_inputed
                                captcha_key=captcha_guessed)
                            print('Posted SUCCESSfully!')
                            update_to_vk_photo_comment_state_group_user_union(postgres_con, postgres_cur,
                                                                              user[1])  # пилять!!!
                            count += 1
                            if bot_sender:
                                bot_sender.day_sent_message_count += 1
                                bot_sender.save()
                            #     if bot_sender.day_sent_message_count == limit_count_of_message:
                            #         break
                            #     # todo ну капец ущербная логика. сделал так только из-за отсутствия времени
                            # if count == limit_count_of_message:
                            #     # здесь прерываем цикл. В случае генератора, возбуждается исключение StopIteration
                            #     # todo странная логика. проверку count нужно вынести в начало цикла
                            #     break
                            time.sleep(delay_between_posts)
                        except:
                            if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
                                print("Неверно ввели каптчу")
                            else:
                                print(erro)
                else:
                    print("Не удалось обработать ошибку и завершить действие")
            time.sleep(delay_between_posts)


def get_important_params(access_token=None):
    # получение объекта аpi при работе из интерфейса
    # todo продумать получение токена из интерфейса при начале отправки
    if access_token:
        # токен получен из бд через представление
        logger.info('{}: получаем api с пом токена из БД: {}'.format(datetime.now(), access_token))
        api = get_api(access_token)
        postgres_con, postgres_cur = connection_to_postgres()
        return api, postgres_con, postgres_cur
    else:
        # токен получаем сейчас с помощью функции и браузера
        access_token, _ = get_saved_auth_params()
        if not access_token or not _:
            access_token, _ = get_auth_params()
        api = get_api(access_token)
        postgres_con, postgres_cur = connection_to_postgres()
        return api, postgres_con, postgres_cur


def main_func():
    access_token, _ = get_saved_auth_params()
    if not access_token or not _:
        access_token, _ = get_auth_params()
    api = get_api(access_token)  # получение "экземпляра апи" по имеющемуся токену

    users = ['368514350']  # список с идентификаторами пользователей
    user_text = "Добрый день, {}! Зацените нашу музыку, но не судите строго))) https://vk.com/gorkyvery"
    for user_id in users:
        # print("User ", user_id)
        # api.wall.post(message="Hello, world")

        # gid = get_user_or_group_info(api, 'gorkyvery')
        get_audio_id(api, gorkiy_group_id)
        time.sleep(60)
        # res = get_user_info(api, ['mozgat'])

        # res = send_message(api, user_id=5567117, message=user_text, attachment=attachments)
        # api.apps.sendRequest(user_id=user_id, text='dddd!!', type='invite')
        # print(api.account.getAppPermissions())
        # create_photo_comment(api, owner_id=users[0], photo_id=416510772, message=user_text, attachments=attachments_for_photo_comment)
        # res = api.users.get(user_id=32007325, fields=['photo_id'])
        print('start!!')
        # print(res)
        # time.sleep(1)
        # print(gid) от 6000 тыс до 7000 не сделал остановился на 15000!! начинать с 16000
        # функЦИЯ для получения подписчиков из VK! И ЗАПИСИ ИХ В БД. Дёргать ЕЁ!!
        # for offset in range(0,2000,1000):
        # res = final_getting_subscribers(api, 'letobar61', offset=offset)
        # time.sleep(0.5)
        # rint(res)
        # print('done')

        '''
        postgres_con, postgres_cur = connection_to_postgres()

        tupl_member_of_group = make_insert_record_to_vk_group_user(res_of_members_of_group)
        make_insert_records_to_vk_group_user_union(postgres_con, postgres_cur, tupl_member_of_group)
        '''

    postgres_con, postgres_cur = connection_to_postgres()
    # tupl_members_inner = select_group_users_from_inner_db(postgres_con, postgres_cur
    # )# our_users # spi_co_mnoy, iowa, mtbarmoscow letobar61
    # tupl_members_inner = select_group_users_union_from_inner_db(postgres_con, postgres_cur)
    #  our_users in group_id# , group_id='iowa'
    tuple_all_users = select_all_users_union_from_inner_db(postgres_con, postgres_cur)
    print(len(tuple_all_users))
    count = 0

    # delete_duplicate_records_of_users_from_db(postgres_con, postgres_cur, tuple_all_users)
    #                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               add_to_friends_with_message(api,  postgres_con, postgres_cur, 'birjabar')
    # final_getting_subscribers_with_offsets_loop(api, 'angelnebes_group')
    # rockbar birjabar letobar61 wundermoscow добавлн весь
    # get_ava_id_and_insert_in_into_db(api, postgres_con, postgres_cur, group_id='artefaq')
    get_settings_of_photo(api, postgres_con, postgres_cur, group_id='zveclub')

    # get_token_by_inner_driver()
    # функция для комментирования (всё вот это ниже)
    gen = do_comment_photo(api, postgres_con, postgres_cur, group_id='lipa48', consider_user_sex=True)
    for i in gen:
        print(i)

    # todo
    # функция для отправки сообщения на стену. owner_id - это владелец стены.
    # res_of_posting_to_wall = post_wall_message(api, group_id='iowa', message='Слушайте новую песню Горького ... https://vk.com/gorkyvery',attachments =attachments)
    # gen = many_posts_wall_message(api, postgres_con, postgres_cur, group_id='mtbarmoscow')
    # for i in gen:
    # print(i)
    # res = api.database.getCountries()

    # res = dir(vk.AuthSession)
    # print(res)
    '''
    #Получить города
    for offset in range(0,10000000,1000):
        list_of_dict_cities = api.database.getCities(country_id = 1, q='Липецк', offset=offset)
        print(list_of_dict_cities)
        if len(list_of_dict_cities) != 0:
            make_and_do_insert_records_to_cities(postgres_con, postgres_cur, list_of_dict_cities)
            time.sleep(0.5)
        else:
            break
    #получить пользователей для города, ЗАРАЗА доступны только первые 1000 результатов
    '''
    '''
    for offset in range(0,400000, 1000):
        city_users = api.users.search(city=78, count=1000, offset=offset)
        print(city_users)
        time.sleep(0.5)
    '''
    # final_sending_privat_message(api, postgres_con, postgres_cur, 'birjabar')


def get_token():
    access_token, _ = get_saved_auth_params()
    if not access_token or not _:
        access_token, _ = get_auth_params()
    api = get_api(access_token)  # получение "экземпляра апи" по имеющемуся токену
    return api


def get_token_from_db_bot(user_id):
    print(user_id)
    access_token, _ = get_saved_auth_params_from_db_bots(user_id)
    print('пришло в эту ветку ф-ии get_token_from_db_bot !!', access_token, _)
    if not access_token or not _:
        access_token, get_auth_params(flag=True)
    api = get_api(access_token)
    return api


if __name__ == '__main__':
    main_func()

id_not = 137799
