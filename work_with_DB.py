__author__ = 'grishaev'

import psycopg2
import settings
import logging
import logging
from datetime import datetime

logger = logging.getLogger('work_with_DB')
logger.setLevel(logging.INFO)


def connection_to_postgres():
    # ДОДЕЛАТЬ!!!
    # получение объектов подключения и курсора к БД
    # есть дублирование кода в APP_INFo
    postgres_con = psycopg2.connect(
        "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(settings.postgres_database_settings['HOST'],
                                                                   settings.postgres_database_settings['DB'],
                                                               settings.postgres_database_settings['USER'],
                                                                   settings.postgres_database_settings['PASSWORD'])
    )

    postgres_cur = postgres_con.cursor()
    return postgres_con, postgres_cur


def select_group_users_union_from_inner_db_for_update(postgres_con, postgres_cur, group_id=None):
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
            # print(result)
            if postgres_cur.statusmessage !=0:
                return result # str(postgres_cur.statusmessage)
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
            # print(result)
            if postgres_cur.statusmessage !=0:
                return result # str(postgres_cur.statusmessage)
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


# запросы для получения статистики ###

def select_count_have_posted_ava_messages(postgres_con, postgres_cur, group_id=None):

    """
    запрашивает количество пользователей ВК, которым отправлены комменты к фото(аватаркам)
    :param postgres_con:
    :param postgres_cur:
    :param group_id:
    :return:
    """

    if group_id is None:
        query = '''
            SELECT count(*) from vk_group_user_union
            WHERE have_post_photo_comment=true
        '''
        try:
            response = postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            # print(result)
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
            postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            # print(result)
            if postgres_cur.statusmessage !=0:
                return result
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


def select_vk_errors(postgres_con, postgres_cur, error_id=None):

    if error_id is None:

        query = '''
            SELECT * from vk_error_text
        '''
        try:
            response = postgres_cur.execute(query)
            result = postgres_cur.fetchall()
            # print(result)
            if postgres_cur.statusmessage != 0:
                return result
        except psycopg2.IntegrityError:
            logging.warning('{}'.format('ОШИБКА ОБРАЩЕНИЯ БД VKSpammer'))


# запросы для обновления

def update_vk_photo_comment_state_group_user_union(postgres_con, postgres_cur, uid, can_post_ava_comment=True) -> None:
    """
    функция для обновления данных по аватаркам в БД
    :param postgres_con:
    :param postgres_cur:
    :param uid:
    :param can_post_ava_comment:
    :return: None
    """
    try:
        if can_post_ava_comment is True:
            query = '''
                UPDATE vk_group_user_union_2
                 SET have_post_photo_comment = true
                  WHERE vk_id={}
            '''
            logger.debug('{} - {}, ставим флаг успешной отправки фото коммента пользователю', datetime.now(), uid)
            # print(tupl_member_of_group[122]['uid'])
            # print(help(postgres_cur.execute))
            postgres_cur.execute(query.format(uid))
            postgres_con.commit()
        else:
            # если возникает исключение, переписываем поле can_post_ava_comment в false
            query = '''
                UPDATE vk_group_user_union_2
                 SET can_post_ava_comment = false
                  WHERE vk_id={}
            '''
            logger.debug('{} - {}, ставим флаг невозможности отправки фото коммента пользователю', datetime.now(), uid)
            # print(tupl_member_of_group[122]['uid'])
            # print(help(postgres_cur.execute))
            postgres_cur.execute(query.format(uid))
            postgres_con.commit()
    except psycopg2.IntegrityError:
        logger.warning('{} - {} - ОШИБКА АПДЕЙТА В БД VKSpammer'.format(datetime.now(), uid))
