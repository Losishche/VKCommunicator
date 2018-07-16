__author__ = 'grishaev'

import psycopg2
import settings
import logging

def connection_to_postgres():
    #ДОДЕЛАТЬ!!!
    #получение объектов подключения и курсора к БД
    #есть дублирование кода в APP_INFo
    postgres_con = psycopg2.connect(
        "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(settings.postgres_database_settings['HOST'],
                                                                   settings.postgres_database_settings['DB'],
                                                               settings.postgres_database_settings['USER'],
                                                                   settings.postgres_database_settings['PASSWORD'])
    )

    postgres_cur = postgres_con.cursor()
    return postgres_con, postgres_cur


def select_group_users_union_from_inner_db_FOR_UPDATE(postgres_con, postgres_cur, group_id=None):
    """
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :param offset:
    :return:
    """
    if group_id and id is None:
        query = '''
            SELECT * FROM vk_group_user_union
                WHERE have_sent_messages is not true and  can_write_private_message=1 for update
        '''
        try:
            response = postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            #print(result)
            if postgres_cur.statusmessage !=0:
                return result #str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))

    else:
        query = '''
            SELECT * FROM vk_group_user_union
                WHERE have_sent_messages is not true AND can_write_private_message=1
                AND vk_group_id='{}' for update
        '''.format(group_id, id)
        try:
            response = postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            #print(result)
            if postgres_cur.statusmessage !=0:
                return result #str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


### запросы для получения статистики ###

def select_count_have_posted_ava_messages(postgres_con, postgres_cur, group_id=None):

    '''
    запрашивает количество пользователей ВК, которым отправлены комменты к фото(аватаркам)
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :return:
    '''

    if group_id is None:
        query = '''
            SELECT count(*) from vk_group_user_union
            WHERE have_post_photo_comment=true
        '''
        try:
            response = postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            #print(result)
            if postgres_cur.statusmessage !=0:
                return result
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))
    else:
        query = '''
            SELECT count(*) from vk_group_user_union
            WHERE have_post_photo_comment=true
            AND vk_group_id = '{}'
        '''.format(group_id)
        try:
            response = postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            #print(result)
            if postgres_cur.statusmessage !=0:
                return result
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def select_vk_errors(postgres_con, postgres_cur, error_id = None):

    if error_id is None:

        query = '''
            SELECT * from vk_error_text
        '''
        try:
            response = postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            #print(result)
            if postgres_cur.statusmessage !=0:
                return result
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))