#!/usr/bin/env python3
import sys
import random
import socket
from selenium.common.exceptions import ElementNotVisibleException as elementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from .VKCommunicatorExceptions import TooFarLastAutorisationException
from multiprocessing import Process
# добавляем путь, где находится backend с бизнес-логикой
pathWithBuisnessLogic = '/home/grishaev/PycharmProjects/VKSpammer/'
sys.path.append(pathWithBuisnessLogic)

from .commenters import *
from .telegram_bot import TelegramBot
from django.shortcuts import render,  HttpResponseRedirect
from .forms import CampParamsForm
from .forms import DoCommentPhotoForm
from .forms import GetTokenForm
from .forms import AskTokenForm
from .forms import EnterGroupIdForm
from .forms import EnterCaptchaForm
from .forms import DoPrivatMessageForm
from .forms import GetStatisticsForm
from .forms import DoWallPostForm, GetAvaInfoAndPhotoSettingsForm, GetSetOfTokensForm, AutorisationForm, DoPrivatMultisenderSendingMessForm
from .forms import MultisenderGetAvaInfoAndPhotoSettingForm, GetUpdatesOfAimGroupForm, DoCommentPhotoMultisenderForm
from .forms import DoCommentPhotoMustiprocMultisendForm, SendMessagesToAimGroupUserForm
from .forms import AddBotsInEachOtherFriendForm, SendMessagesToFriendsPrivateForm
from .forms import MakeDistributionThroughFakeBrowserForm, GetAimGroupWallPostsForm, LikeAimGroupPostsForm
from _datetime import datetime
from django.utils import timezone
from time import sleep
from work_with_vk_friends import MessageToPrivateSender
from app_info import parse_and_save_auth_params
from app_info import  get_token_by_inner_driver, get_auth_params_from_interface, autentification_in_vk_via_web_dr
from app_info import final_sending_privat_message, get_ava_id_and_insert_in_into_db, get_settings_of_photo, do_comment_photo, many_posts_wall_message
from app_info import final_getting_subscribers_with_offsets_loop
from app_info import get_important_params
from app_info import logger, proccess_log_file_path
from app_info import final_sending_privat_message_with_multisender
from app_info import multiproc_do_comment_photo, multiproc_get_photo_params
from app_info import add_bots_to_friends_of_each_other
from app_info import get_wall_posts
from app_info import vk_api_version
from app_info import day_ava_message_limit
# from app_info import attachments # todo временное
# from work_with_DB import select_count_have_posted_ava_messages
from work_with_DB import connection_to_postgres
from .models import VkGroupUserUnion2, BotsSenders, CampParams, AvaMessages, VKApplications, GorkiyGroupUser, \
    PrivateMessages, BotsFriends, InvitePrivateMessages, InviteMessagesToLoyalGroupUsers, VkWallPosts
from django.core.exceptions import ObjectDoesNotExist
# from app_info import do_comment_photo
from .selenium_sender import SeleniumSender
from .vk_notifications_api import VkNotifications

# vk_api_version = '5.00'
# proccess_log_file_path =
# '/home/grishaev/PycharmProjects/VKSpammer/VKSpammer/VKSpam_djg/static/VKSpam_djg/process_log.txt'
logger = logging.getLogger('logger_view_communicator')
logger.setLevel(logging.INFO)
# fh = logging.FileHandler(proccess_log_file_path)
# fh.setLevel(logging.INFO)
# logger_for_communicator.addHandler(fh)

# logging.basicConfig(level=logging.INFO)


def index(request):
    context = {}
    if request.method == 'POST':
        logging.info('обработали запрос')
        get_token_form = GetTokenForm(request.POST)
        # ask_token_form = AskTokenForm(request.POST)
        enter_group_id_form = EnterGroupIdForm(request.POST)
        do_comment_photo_form = DoCommentPhotoForm(request.POST)
        enter_captcha_form = EnterCaptchaForm(request.POST)
        do_wall_post_form = DoWallPostForm(request.POST)
        do_privat_message_form = DoPrivatMessageForm(request.POST)

        # logging.debug(get_token_form.is_valid())
        # logging.debug(ask_token_form.is_valid())
        logger.info('{}: '.format(datetime.now(), request.POST))
        print(request.POST)
        if get_token_form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            user_token = get_token_form.cleaned_data.get('user_token')
            parsed_token, vk_user_id, expires_in = parse_and_save_auth_params(user_token)
            try:
                sender = BotsSenders.objects.get(vk_user_id=vk_user_id)
            except BotsSenders.DoesNotExist:
                sender = False
            if sender:
                sender.vk_token = parsed_token
                sender.save()
            logger.info("{} - обработали полученный токен: {}".format(datetime.now(), parsed_token))
            context['result_of_handling_token_string'] = "Токен успешно загружен в программу " + parsed_token
            # return HttpResponseRedirect('/thanks/')
            # elif request.POST.get('ask_token_btn'): хз, но почему-то изменилось ПОСЛЕ ДОБАВЛЕНИЯ CSS((
            # result = request.POST.get('ask_token_btn')#

        elif request.POST.get('take_token'):
            result = request.POST.get('take_token')
            logging.info(result)
            # хардкодим процесс, порождающий рандомное использование нескольких приложений
            vk_app_list= VKApplications.objects.all()
            vk_app_id = vk_app_list.get(id=random.randint(1, len(vk_app_list))).vk_app_id
            if result is not False:  # сознательное дублирование изначального условия
                get_auth_params_from_interface(vk_app_id)

        elif request.POST.get('take_all_token_automatically'):
            request.POST.get('take_all_token_automatically')
            for bot in BotsSenders.objects.all():
                get_token_by_inner_driver(bot.vk_login, bot.vk_password)

        elif enter_group_id_form.is_valid():
            group_id_to_insert = enter_group_id_form.cleaned_data.get('inputed_group_id')
            logging.info(group_id_to_insert)
            api, conn, cur = get_important_params()
            result = final_getting_subscribers_with_offsets_loop(api, group_id_to_insert)
            if result == 'OK':
                context['status_for_getting_subscribers'] = \
                    enter_group_id_form.status_for_getting_subscribers.format(group_id_to_insert)
        # чтобы работать с формой, нужно выполнить ф-ю is_valid!!!
        elif do_comment_photo_form.is_valid():
            vk_group_id = do_comment_photo_form.cleaned_data.get('vk_group_id')  # потому что словарь!
            message = do_comment_photo_form.cleaned_data['message']  # потому что словарь!
            # message = do_comment_photo_form.message
            print('тут что-то происходит, а не должно при нажатии кнопки загрузить', vk_group_id, message)
            # api, postgres_con, postgres_cur = get_important_params()
            # generator_for_commenting = do_comment_photo(
            # api, postgres_con, postgres_cur, vk_group_id, consider_user_sex=True, is_run_from_interface=True)
            # todo костыльные внутренние серверы блин

            sock = socket.socket()
            sock.connect(('localhost', 9092))
            # sock.send(b'start_generator')
            # data = sock.recv(10244)
            open_signal = bytes('start_commenting_photo', encoding='utf8')
            # print(message)
            sock.send(open_signal)
            data = sock.recv(1024)
            if data == b'start_commenting_photo_resp':
                parameters = vk_group_id + ', ' + message
                parameters = bytes(parameters, encoding='utf8')
                sock.send(parameters)
                context['status_for_start_of_posting_ava_comment'] = \
                    do_comment_photo_form.status_for_start_of_posting_ava_comment
                data = sock.recv(1024)
                if data == b'cought_exeption':
                    context['status_for_cought_exeption'] = '!!!!'

            print(data)
            if data == 'end':
                # sock.close()
                context['status_for_finish_of_posting_ava_comment'] = \
                    do_comment_photo_form.status_for_finish_of_posting_ava_comment
            elif data == 'unknown_parameter':
                sock.close()

            '''for gen_result in generator_for_commenting:
                if gen_result == 'handling_exception':
                    #todo всплывающее окно нужно ли всплывающее окно???
                    inputed_captcha = input()
                    print('принята капча', inputed_captcha)
                    generator_for_commenting.send(inputed_captcha)
            '''
        elif do_wall_post_form.is_valid():
            # ветка для постов на стенку
            # метод cleaned data возвращает словарь!
            vk_group_id_for_wall_post = do_wall_post_form.cleaned_data.get('vk_group_id_for_wall_post')
            wall_post = do_wall_post_form.cleaned_data['wall_post'] # потому что словарь!
            # todo подумать на счёт портов
            sock = socket.socket()
            sock.connect(('localhost', 9093))
            open_signal = bytes('start_posting_wall_comments', encoding='utf8')
            # print(message)
            sock.send(open_signal)
            data = sock.recv(1024)
            print(data)
            logger.info('{}: data'.format(datetime.time()))
            if data == b'start_posting_wall_comments_resp':

                attachments = str(['audio-41360940_426516897',
                                   'audio-41360940_327478545',
                                   'audio-41360940_456239024',
                                   'audio-41360940_456239025',
                                   'photo-41360940_378305307'])
                print(vk_group_id_for_wall_post, wall_post, attachments)
                parameters = vk_group_id_for_wall_post + ', ' + wall_post + ', ' + attachments
                print(parameters)
                parameters = bytes(parameters, encoding='utf8')
                sock.send(parameters)
            context['status_for_start_of_wall_post'] = do_wall_post_form.status_for_start_of_wall_post
            print(data)
            if data == 'end_wall_posting':
                # sock.close()
                context['status_for_finish_of_wall_post'] = do_wall_post_form.status_for_finish_of_wall_post
            elif data == 'unknown_parameter':
                sock.close()

        elif enter_captcha_form.is_valid():
            inputed_captcha = enter_captcha_form.cleaned_data.get('inputed_captcha')
            kind_of_distribution = enter_captcha_form.cleaned_data.get('kind_of_distribution')
            print('ввели капчу', inputed_captcha)
            if kind_of_distribution is False:
                sock = socket.socket()
                sock.connect(('localhost', 9092))
            elif kind_of_distribution is True:
                sock = socket.socket()
                sock.connect(('localhost', 9093))
            else:
                # по умолчанию
                sock = socket.socket()

            print("посылаем send из ветки enter_captcha")
            sock.send(b'catch_exception')
            response_data = sock.recv(1024)
            if response_data == b'handling_exception':
                print("ЗДЕЕЕЕЕСЬ ОТСЫЛАЕТСЯ КАПЧА!!")
                inputed_captcha_encode_to_send = bytes(inputed_captcha, encoding='utf8')
                sock.send(inputed_captcha_encode_to_send)
                # добавляем в контекст переменную
                context['captcha_inf']=enter_captcha_form.captcha_inf.format(inputed_captcha)
                response_data = sock.recv(1024)
                response_data = response_data.decode('utf8')
                print(response_data)
                if response_data == 'end':
                    context['status_for_finish_of_posting_ava_comment'] = \
                        do_comment_photo_form.status_for_finish_of_posting_ava_comment
                if response_data == 'end_wall_posting':
                    context['status_for_finish_of_wall_post'] = do_wall_post_form.status_for_finish_of_wall_post

        elif do_privat_message_form.is_valid():
            vk_group_id_2 = do_privat_message_form.cleaned_data.get('vk_group_id_2')
            do_privat_message_form.cleaned_data['privat_message']
            api, conn, cur = get_important_params()
            print(vk_group_id_2)
            final_sending_privat_message(api, conn, cur, vk_group_id_2)
        else:
            result_of_hangling_token_string = "Неверный URL "
            context['result_of_hangling_token_string'] = result_of_hangling_token_string

    logging.info('конечная ветка')
    ask_token_form = AskTokenForm()
    form_to_get_user_token = GetTokenForm()
    enter_group_id_form = EnterGroupIdForm()
    do_comment_photo_form = DoCommentPhotoForm()
    enter_captcha_form = EnterCaptchaForm()
    do_wall_post_form = DoWallPostForm()
    do_privat_message_form = DoPrivatMessageForm()
    # form_for_subscribed_statistic = GetMessageTextForm()
    context['ask_token_form'] = ask_token_form
    context['form_to_get_user_token'] = form_to_get_user_token
    context['enter_group_id_form'] = enter_group_id_form
    context['do_comment_photo_form'] = do_comment_photo_form
    context['enter_captcha_form'] = enter_captcha_form
    context['do_wall_post_form'] = do_wall_post_form
    context['do_privat_message_form'] = do_privat_message_form

    # передаем ЗАПРОС, ШАБЛОН и КОНТЕКСТ (словарь переменных с объектами)
    return render(request, 'VKSpam_djg/index.html', context)

    # функция render() первым аргументом принимает объект запроса, также название шаблона и
    # необязательный словарь значений контекста.
    # Возвращает объект HttpResponse содержащий выполненный шаблон с указанным контексто


def statistics(request, group_id=None):

    context = {}
    if request.method == 'POST':
        # print('отладка')
        get_statistics_form = GetStatisticsForm(request.POST)
        if get_statistics_form.is_valid():
            # print('отладка2')
            choice_id = get_statistics_form.cleaned_data.get('CHOICES_FOR_KIND_OF_SENDING')
            print(choice_id)
            group_id = get_statistics_form.cleaned_data.get('vk_group_id_3')
            context['group_id'] = group_id
            if choice_id == '1':
                print('отладка 2')
                # postgres_con, postgres_cur =
                # select_count_have_posted_ava_messages(postgres_con, postgres_cur, group_id=group_id)
                count_of_photo_comment_posted = VkGroupUserUnion2.objects.filter(
                    vk_group_id=group_id,
                    have_post_photo_comment=True
                ).count()
                context['count_of_photo_comment_posted'] = count_of_photo_comment_posted

            elif choice_id == '2':
                # postgres_con, postgres_cur =
                # select_count_have_posted_ava_messages(postgres_con, postgres_cur, group_id=group_id)
                count_of_privat_message_sent = VkGroupUserUnion2.objects.filter(
                    vk_group_id=group_id,
                    have_sent_messages=1
                ).count()
                context['count_of_privat_message_sent'] = count_of_privat_message_sent

            elif choice_id == '3':
                count_of_group_subscribers = VkGroupUserUnion2.objects.filter(vk_group_id=group_id).count()
                print(count_of_group_subscribers)
                context['count_of_group_subscribers'] = count_of_group_subscribers

            elif choice_id == '4':
                count_of_photo_comment_posted = \
                    VkGroupUserUnion2.objects.filter(vk_group_id=group_id, have_post_photo_comment=True).count()
                context['count_of_photo_comment_posted'] = \
                    count_of_photo_comment_posted
                count_of_privat_message_sent = \
                    VkGroupUserUnion2.objects.filter(vk_group_id=group_id, have_sent_messages=1).count()
                context['count_of_privat_message_sent'] = \
                    count_of_privat_message_sent
                count_of_wall_post_sent = \
                    VkGroupUserUnion2.objects.filter(vk_group_id=group_id, have_post_wall_comment=True).count()
                context['count_of_wall_post_sent'] = \
                    count_of_wall_post_sent
                count_of_group_subscribers = \
                    VkGroupUserUnion2.objects.filter(vk_group_id=group_id).count()
                context['count_of_group_subscribers'] = \
                    count_of_group_subscribers
                count_of_possible_ava_comment = \
                    VkGroupUserUnion2.objects.filter(vk_group_id=group_id, can_post_ava_comment=True).count()
                context['count_of_possible_ava_comment'] = \
                    count_of_possible_ava_comment
                count_of_possible_privat_message = \
                    VkGroupUserUnion2.objects.filter(vk_group_id=group_id, can_write_private_message=1).count()
                context['count_of_possible_privat_message'] = \
                    count_of_possible_privat_message
                # count_of_all_sent_messages_and_posts = VkGroupUserUnion.objects.filter(
                #    vk_group_id=group_id,
                #    have_post_ava_comment=1).count()
                # context['count_of_all_sent_messages_and_posts'] = count_of_all_sent_messages_and_posts

    get_statistics_form = GetStatisticsForm()
    context['get_statistics_form'] = get_statistics_form
    return render(request, 'VKSpam_djg/statistics.html', context)


def get_bots_and_apis():
    set_of_senders = BotsSenders.objects.filter(is_blocked=False)
    users_api = []
    print('{}: получение ботов для мультипроцессинга'.format(datetime.now()))
    for bot in set_of_senders:
        print('start distr with token', bot.surname, bot.vk_login)
        logger.info('start distr with bot: {}, {}'.format(bot.surname, bot.name))
        # date_offset = NaiveTZInfo(+3)
        if bot.date_of_starting_day_counting is None:
            bot.date_of_starting_day_counting = timezone.now()
            bot.save()

        if (timezone.now() - bot.date_of_starting_day_counting).days >= 1:
            bot.date_of_starting_day_counting = timezone.now()
            bot.day_sent_message_count = 0
            bot.save()
            # чёрт знаёт что! все преобразовывается в списки!
            # todo позумать, как можно убрать дополнительные преобразования в списки
            users_api.append(list(get_important_params(bot.vk_token)) + [bot])
            # api, conn, cur = get_important_params(bot.vk_token)

            # чёрт знает какая логика!!! тут прямо в функцию, в else - через внут.сервер!!!
        if (timezone.now() - bot.date_of_starting_day_counting).days < 1 \
                and bot.day_sent_message_count < day_ava_message_limit:
            api, conn, cur = get_important_params(bot.vk_token)
            # texts = AvaMessages.objects
            users_api.append(list(get_important_params(bot.vk_token)) + [bot])

    return users_api


def _execute_distribution_with_one_sender_with_strategy(do_comment_photo_form, context):
    vk_group_id = do_comment_photo_form.cleaned_data.get('vk_group_id')  # потому что словарь!
    message = do_comment_photo_form.cleaned_data['message']
    is_autocaptcha = do_comment_photo_form.cleaned_data.get('is_autocaptcha')
    is_sex_considered = do_comment_photo_form.cleaned_data.get('is_sex_considered')
    bots_sender_name = do_comment_photo_form.cleaned_data.get('bots_senders')
    is_multitext = do_comment_photo_form.cleaned_data.get('is_multitext')
    # message = do_comment_photo_form.message
    print('starting work with group: {}, message: \'{}\', sender: {}', vk_group_id, message, bots_sender_name)
    # пишет в лог для отображения в интерфейсе
    logger.info(
        'starting work with group: {}, message: \'{}\', sender: {}'.format(vk_group_id, message, bots_sender_name))
    # api, postgres_con, postgres_cur = get_important_params()
    # generator_for_commenting = do_comment_photo(
    # api, postgres_con, postgres_cur, vk_group_id, consider_user_sex=True, is_run_from_interface=True)
    # todo костыльные внутренние серверы блин

    sock = socket.socket()
    sock.connect(('localhost', 9092))
    print('{} - автокапча активирована? {}'.format(datetime.now(), is_autocaptcha))
    logger.info('{} - автокапча активирована? {}'.format(datetime.now(), is_autocaptcha))

    bot_sender = BotsSenders.objects.get(vk_user_id=bots_sender_name)
    user_token = bot_sender.vk_token
    # работа напрямую с функцией backend
    # if BotsSenders.object.get()
    print(datetime.now(), 'start distr with user and token', bot_sender, user_token)
    logger.info('{} - start distr with user: {} and token: {}'.format(
        datetime.now(), bot_sender, user_token)
    )
    if is_autocaptcha:
        # доделать стратегии для отправки без автокапчи
        commenter = Commenter(bot_sender, vk_group_id, is_autocaptcha, is_sex_considered, is_multitext)
        commenter.strategy.post_photo_comment()
        sock.close()
    else:
        # работа через внутренний сервер!!!!
        open_signal = bytes('start_commenting_photo', encoding='utf8')
        # print(message)
        sock.send(open_signal)
        data = sock.recv(1024)
        if data == b'start_commenting_photo_resp':
            parameters = vk_group_id + ', ' + message
            parameters = bytes(parameters, encoding='utf8')
            sock.send(parameters)
            context['status_for_start_of_posting_ava_comment'] = \
                do_comment_photo_form.status_for_start_of_posting_ava_comment
            data = sock.recv(1024)
            # std_out_messages = open('/home/grishaev/PycharmProjects/VKSpammer/test_stdout')
            std_out_messages = open('../test_stdout')
            context['std_out_messages'] = std_out_messages.readline()
            if data == b'cought_exeption':
                context['status_for_cought_exeption'] = '!!!!'  # что ЭТО такое??
        print("{} - значение протокола, полученное от 'внутреннего сервера': {}".format(datetime.now(), data))
        if data == 'end':
            # sock.close()
            context['status_for_finish_of_posting_ava_comment'] = \
                do_comment_photo_form.status_for_finish_of_posting_ava_comment
        elif data == 'unknown_parameter':
            sock.close()


def distr_to_avas(request):
    context = {}
    with open(proccess_log_file_path, 'w'):
        pass
    temp_stdout = sys.stdout
    # sys.stdout = open(proccess_log_file_path, 'w')
    if request.method == 'POST':
        logger.info('{} - обработали запрос на старт рассылки по аватаркам'.format(datetime.now()))
        # create a form instance and populate it with data from the request:
        do_comment_photo_form = DoCommentPhotoForm(request.POST)
        do_comment_photo_multisender_form = DoCommentPhotoMultisenderForm(request.POST)
        do_comment_photo_mustiproc_multisend_form = DoCommentPhotoMustiprocMultisendForm(request.POST)
        EnterCaptchaForm(request.POST)
        print(do_comment_photo_mustiproc_multisend_form.is_valid(),
              do_comment_photo_mustiproc_multisend_form.cleaned_data
              )
        print(do_comment_photo_multisender_form.is_valid(),  do_comment_photo_multisender_form.cleaned_data)
        # sleep(300)
        logger.info('{} - is form valid? {}'.format(datetime.now(), do_comment_photo_form.is_valid()))
        if do_comment_photo_form.is_valid():  # чтобы работать с формой, нужно выполнить ф-ю is_valid!!!
            _execute_distribution_with_one_sender_with_strategy(do_comment_photo_form, context)

        elif do_comment_photo_multisender_form.is_valid():  # чтобы работать с формой, нужно выполнить ф-ю is_valid!!!
            vk_group_id = do_comment_photo_multisender_form.cleaned_data.get('vk_group_id')
            starting_sender = BotsSenders.objects.filter(is_blocked=False).order_by("id")[20:]
            # users_api = []
            print('{} - пришло на ветку с мультисендером, но без мультипроцессинга, '
                  'starting_sender пока игнорируется'.format(datetime.now()))
            commenter = Commenter(starting_sender, vk_group_id, True, False, True, True)
            commenter.strategy.post_photo_comment()

        elif do_comment_photo_mustiproc_multisend_form.is_valid():
            # todo избыточное дублирование кода из предыдущего условия ДЛЯ НАГЛЯДНОСТИ!!!
            # todo чтобы убрать, нужно проверку даты отправки и исчерпания дневных лимитов вынести в отдельную функцию
            vk_group_id = do_comment_photo_mustiproc_multisend_form.cleaned_data.get('vk_group_id_for_mp')
            is_sex_considered = do_comment_photo_mustiproc_multisend_form.cleaned_data.get('is_sex_considered')
            set_of_senders = BotsSenders.objects.filter(is_blocked=False)
            users_api = []
            print('пришло на ветку с мультипроцессингом')
            for bot in set_of_senders:
                print('start distr with token', bot.surname, bot.vk_login)
                logger.info('start distr with bot: {}, {}'.format(bot.surname, bot.name))
                # date_offset = NaiveTZInfo(+3)
                if bot.date_of_starting_day_counting is None:
                    bot.date_of_starting_day_counting = timezone.now()
                    bot.save()

                if (timezone.now() - bot.date_of_starting_day_counting).days >= 1:
                    bot.date_of_starting_day_counting = timezone.now()
                    bot.day_sent_message_count = 0
                    bot.save()
                    # чёрт знаёт что! все преобразовывается в списки!
                    # todo подумать, как можно убрать дополнительные преобразования в списки
                    users_api.append(list(get_important_params(bot.vk_token)) + [bot])
                    # api, conn, cur = get_important_params(bot.vk_token)

                if (timezone.now() - bot.date_of_starting_day_counting).days < 1 and bot.day_sent_message_count < 90:
                    api, conn, cur = get_important_params(bot.vk_token)
                    # texts = AvaMessages.objects
                    users_api.append(list(get_important_params(bot.vk_token)) + [bot])
                else:
                    logger.info(
                        '{}: дневной лимит для пользователя "{}" исчерпан'.format(datetime.now(), bot.surname)
                    )
                    print('{}: дневной лимит для пользователя "{}" исчерпан'.format(datetime.now(), bot.surname))
            print(users_api)
            # sleep(300)
            texts = AvaMessages.objects
            if is_sex_considered:
                multiproc_do_comment_photo(
                    users_api,
                    conn,
                    cur,
                    vk_group_id,
                    consider_user_sex=is_sex_considered,
                    is_run_from_interface=True,
                    auto_captcha=True,
                    is_multitext=texts,
                    # bot_sender = api_u[3]
                )
            else:
                multiproc_do_comment_photo(
                    users_api,
                    conn,
                    cur,
                    vk_group_id,
                    consider_user_sex=False,
                    is_run_from_interface=True,
                    auto_captcha=True,
                    is_multitext=texts,
                    # bot_sender = api_u[3],
                )
    do_comment_photo_form = DoCommentPhotoForm()
    enter_captcha_form = EnterCaptchaForm()
    do_comment_photo_multisender_form = DoCommentPhotoMultisenderForm()
    do_comment_photo_mustiproc_multisend_form = DoCommentPhotoMustiprocMultisendForm()
    context['do_comment_photo_form'] = do_comment_photo_form
    context['do_comment_photo_multisender_form'] = do_comment_photo_multisender_form
    context['do_comment_photo_mustiproc_multisend_form'] = do_comment_photo_mustiproc_multisend_form
    context['enter_captcha_form'] = enter_captcha_form

    return render(request, 'VKSpam_djg/distr_to_avas.html', context)


def works_with_groups(request):
    context = {}
    if request.method == 'POST':
        logging.info('обработали запрос works_with_groups')
        get_ava_info_and_photo_settings_form = GetAvaInfoAndPhotoSettingsForm(request.POST)
        multisender_get_ava_info_and_photo_setting_form = MultisenderGetAvaInfoAndPhotoSettingForm(request.POST)
        if get_ava_info_and_photo_settings_form.is_valid():
            print(dir(get_ava_info_and_photo_settings_form))
            # sleep(300)
            vk_gr_id_for_getting_settings = get_ava_info_and_photo_settings_form.cleaned_data.get('vk_group_id')
            api, postgres_con, postgres_cur = get_important_params()
            # get_ava_id_and_insert_in_into_db(api, postgres_con, postgres_cur, group_id=vk_gr_id_for_getting_settings)
            get_settings_of_photo(api, postgres_con, postgres_cur, group_id=vk_gr_id_for_getting_settings)

        elif multisender_get_ava_info_and_photo_setting_form.is_valid():
            vk_gr_id_for_getting_settings = multisender_get_ava_info_and_photo_setting_form.cleaned_data.get(
                'vk_group_id_multisender_g_a_i_a_p_s_f'
            )
            bots_apis = get_bots_and_apis()
            multiproc_get_photo_params(bots_apis, vk_gr_id_for_getting_settings, True)
            '''
            for bot in BotsSenders.objects.all():
                offset += 1000
                print('работаем с пользователем: ', bot.surname)
                api, postgres_con, postgres_cur = get_important_params(access_token=bot.vk_token)
                p = Process(target = get_subscriber_settings_with_multisender_and_multiproc, args=(queue, api, min_value, offset))
                allProcess.append(p)
                #p.start()
                min_value += offset
                print('создали!')

                print(allProcess)

            for p in allProcess:
                 p.start()'''

    get_ava_info_and_photo_settings_form = GetAvaInfoAndPhotoSettingsForm(request.GET)
    multisender_get_ava_info_and_photo_setting_form = MultisenderGetAvaInfoAndPhotoSettingForm()
    context['get_ava_info_and_photo_settings_form'] = get_ava_info_and_photo_settings_form
    context['multisender_get_ava_info_and_photo_setting_form'] = multisender_get_ava_info_and_photo_setting_form
    return render(request, 'VKSpam_djg/works_with_groups.html', context)


def distr_to_walls(request):
    context = {}
    if request.method == 'POST':
        logging.info('обработали запрос')
        do_wall_post_form = DoWallPostForm(request.POST)
        if do_wall_post_form.is_valid():
            # ветка для постов на стенку
            vk_group_id_for_wall_post = do_wall_post_form.cleaned_data.get('vk_group_id')  # потому что словарь!
            wall_post = do_wall_post_form.cleaned_data['wall_post']  # потому что словарь!
            is_autocaptcha = do_wall_post_form.cleaned_data.get('is_autocaptcha')
            bots_sender = do_wall_post_form.cleaned_data.get('bots_senders')
            print(vk_group_id_for_wall_post, is_autocaptcha)
            if is_autocaptcha:
                if bots_sender:
                    user_token = BotsSenders.objects.get(vk_user_id=bots_sender).vk_token
                    # работа напрямую с функцией backend
                    print('start distr_to_walls with old token', user_token)
                    api, postgres_con, postgres_cur = get_important_params(user_token)
                    # api, postgres_con, postgres_cur = get_important_params()
                    gen_cp = many_posts_wall_message(api,
                                                     postgres_con,
                                                     postgres_cur,
                                                     vk_group_id_for_wall_post,
                                                     is_run_from_interface=True,
                                                     auto_captcha=True)
                    # выше чёрт знает какая логика!!! тут прямо в функцию, в else - через внут.сервер!!!
                    for item in gen_cp:
                        print(item)
            else:
                # работа через внутренний сервер!!!!
                # todo подумать на счёт портов
                sock = socket.socket()
                sock.connect(('localhost', 9093))
                open_signal = bytes('start_posting_wall_comments', encoding='utf8')
                # print(message)
                sock.send(open_signal)
                data = sock.recv(1024)
                print(data)
                if data == b'start_posting_wall_comments_resp':

                    attachments = str(['audio-41360940_426516897',
                                       'audio-41360940_327478545',
                                       'audio-41360940_456239024',
                                       'audio-41360940_456239025',
                                       'photo-41360940_378305307'])
                    print(vk_group_id_for_wall_post, wall_post, attachments)
                    parameters = vk_group_id_for_wall_post + ', ' + wall_post + ', ' + attachments
                    print(parameters)
                    parameters = bytes(parameters, encoding='utf8')
                    sock.send(parameters)
                context['status_for_start_of_wall_post'] = do_wall_post_form.status_for_start_of_wall_post
                print(data)
                if data == 'end_wall_posting':
                    # sock.close()
                    context['status_for_finish_of_wall_post'] = do_wall_post_form.status_for_finish_of_wall_post
                elif data == 'unknown_parameter':
                    sock.close()
    # конечная ветка
    do_wall_post_form = DoWallPostForm()
    enter_captcha_form = EnterCaptchaForm()
    context['do_wall_post_form'] = do_wall_post_form
    context['enter_captcha_form'] = enter_captcha_form
    return render(request, 'VKSpam_djg/distr_to_walls.html', context)


def distr_to_privat(request):
    context = {}
    if request.method == 'POST':
        logging.info('обработали запрос')
        do_privat_message_form = DoPrivatMessageForm(request.POST)
        do_privat_multisender_sending_mess_form = DoPrivatMultisenderSendingMessForm(request.POST)

        if do_privat_message_form.is_valid():
            # ветка для отправки в личку
            print(do_privat_message_form)
            vk_group_id_for_privat_ms = do_privat_message_form.cleaned_data.get('vk_group_id_2')
            api, conn, cur = get_important_params()
            print(vk_group_id_for_privat_ms)

            final_sending_privat_message(api, conn, cur, vk_group_id_for_privat_ms)
            context['status_for_start_of_privat_distr'] = \
                do_privat_message_form.status_for_start_of_sending_privat_messages

        elif do_privat_multisender_sending_mess_form.is_valid():
            # ветка для отправки в личку от имеющегося множества сендеров последовательно
            print('Отправка в режиме Мультисендер')
            vk_group_id_for_privat_ms = \
                do_privat_multisender_sending_mess_form.cleaned_data.get('vk_group_id_multisender')
            print(vk_group_id_for_privat_ms)
            obj_of_privat_messages = PrivateMessages.objects.all()
            text_list_for_multitext = [obj.message for obj in PrivateMessages.objects.all()]
            count_of_end_work = 2
            for bot in BotsSenders.objects.all():
                if not bot.is_blocked:
                    text_list_for_bot = []
                    for i in range(0, count_of_end_work):
                        text_list_for_bot.append(
                            text_list_for_multitext[random.randint(0, len(text_list_for_multitext)-1)])
                        i += 1
                    access_token = bot.vk_token
                    # todo возможно следует хранить api-объект пользователя??
                    print(text_list_for_bot)
                    api, conn, cur = get_important_params(access_token)
                    print('получили объект api, вызываем функцию')
                    final_sending_privat_message_with_multisender(
                        api,
                        conn,
                        cur,
                        vk_group_id_for_privat_ms,
                        text_list_for_bot,
                        count_of_end_work=count_of_end_work
                    )

    do_privat_message_form = DoPrivatMessageForm()
    do_privat_multisender_sending_mess_form = DoPrivatMultisenderSendingMessForm()
    send_messages_to_friends_private_form = SendMessagesToFriendsPrivateForm()
    send_messages_to_aim_group_user_form = SendMessagesToAimGroupUserForm()
    make_distribution_through_fake_browser_form = MakeDistributionThroughFakeBrowserForm()
    context['do_privat_message_form'] = do_privat_message_form
    context['do_privat_multisender_sending_mess_form'] = do_privat_multisender_sending_mess_form
    context['send_messages_to_friends_private_form'] = send_messages_to_friends_private_form
    context['send_messages_to_aim_group_user_form'] = send_messages_to_aim_group_user_form
    context['make_distribution_through_fake_browser_form'] = make_distribution_through_fake_browser_form
    return render(request, 'VKSpam_djg/distr_to_privat.html', context)


def _get_user_info(api, vk_sender):
    """
    получение информации о пользователе
    :return:
    """
    friends_ids_list = api.friends.get(version=vk_api_version)
    friends_from_vk = api.users.get(version=vk_api_version, user_ids=friends_ids_list)
    print(friends_from_vk)
    for friend in friends_from_vk:
        bot_friend = BotsFriends()
        bot_friend.vk_user_id = friend['uid']
        bot_friend.first_name = friend['first_name']
        bot_friend.last_name = friend['last_name']
        bot_friend.friend_bot = vk_sender
        print("{}: получен друг: {}".format(datetime.now(), bot_friend))
        bot_friend.save()
    # friends_list = BotsFriends.objects.get()


# ###Представление для запуска рассылки в личку по друзьям Сендера###
def make_distribution_to_friends_private(request):
    context = {}
    if request.method == 'POST':
        logger.info("{}: запрос на рассылку в личку друзей".format(datetime.now()))
        send_messages_to_friends_private_form = SendMessagesToFriendsPrivateForm(request.POST)
        if send_messages_to_friends_private_form.is_valid():
            # ветка для отправки в личку
            logger.info("{}: обработали форму, {}".format({}, send_messages_to_friends_private_form))
            vk_sender = send_messages_to_friends_private_form.cleaned_data.get('vk_senders')
            logger.info("{}: выбран сендер: {}".format(datetime.now(), vk_sender))
            logging.info("{}: выбран сендер: {}".format(datetime.now(), vk_sender))
            sender_object = BotsSenders.objects.get(vk_user_id=int(vk_sender))
            print("sender object", sender_object)
            api, conn, cur = get_important_params(sender_object.vk_token)
            logger.info("{}: сообщения будут отправлены друзьям Сендера: {}".format(datetime.now(), sender_object))
            # глупо делать классы в джава-стиле хотя бы потому, что нельзя их напрямую вызывать
            # без указания "модуля"

            # блок для получения друзей Сендера
            try:
                print("получаем друзей Сендера из БД")
                friends_list = BotsFriends.objects.filter(friend_bot=sender_object)
                if len(friends_list) == 0:
                    print("друзей Сендера в БД не обнаружено, получаем из ВК")
                    _get_user_info(api, sender_object)
                    friends_list = BotsFriends.objects.filter(friend_bot=sender_object)
            except ObjectDoesNotExist:
                _get_user_info(api, sender_object)
                friends_list = BotsFriends.objects.filter(friend_bot=sender_object)

            # sleep(300)
            message_to_private_sender = MessageToPrivateSender.MessageToPrivateSender(
                api,
                conn,
                cur,
                friends_list,
                vk_sender
            )
            messages_object = InvitePrivateMessages.objects.all()
            message_to_private_sender.send_invite_messages([m_object.message for m_object in messages_object])
            sleep(30)
            # message_to_private_sender.send_invite_messages()
            context['status_of_sending_privat_messages'] = \
                send_messages_to_friends_private_form.status_of_sending_privat_messages


# def make_distribution_to_friendly_group_users_through_fake_browser(request):
#     context = {}
#     if request.method == 'POST':
#         logger_for_communicator.info(
#             "запрос на рассылку по личкам пользователей дружественной группы "
#             "посредсвом фейкового браузера".format(datetime.now())
#         )
#         send_messages_form = SendMessagesToAimGroupUserThroughFakeBrowserForm(request.POST)
#         if send_messages_form.is_valid():
#             logger_for_communicator.info("{}: обработали форму, {}".format({}, send_messages_form))


# todo метод поломан
def make_distribution_to_aim_group_through_private_messages(request):
    logger.info(request)
    context = {}
    if request.method == 'POST':
        logger.info(
            "запрос на рассылку по личкам пользователей дружественной группы".format(datetime.now())
        )
        send_messages_to_aim_group_user_form = SendMessagesToAimGroupUserForm(request.POST)

        if send_messages_to_aim_group_user_form.is_valid():
            logger.info("{}: обработали форму, {}".format({}, send_messages_to_aim_group_user_form))
            vk_sender = send_messages_to_aim_group_user_form.cleaned_data.get('vk_senders')
            logger.info("{}: выбран сендер: {}".format(datetime.now(), vk_sender))
            logging.info("{}: выбран сендер: {}".format(datetime.now(), vk_sender))
            sender_object = BotsSenders.objects.get(vk_user_id=int(vk_sender))

            logger.info("Сендер для рассылки: {}".format(sender_object))
            api, conn, cur = get_important_params(sender_object.vk_token)
            logger.info(
                "{}: сообщения будут отправлены друзьям Сендера: {}".format(datetime.now(), sender_object)
            )

            # выдёргиваем подписчиков из бд
            users_set = set(GorkiyGroupUser.objects
                            .filter(have_sent_invite_private_message=None)
                            .exclude(can_write_private_message=0))
            bots_friends_set = set(BotsFriends.objects.all())
            users_list = list(users_set.difference(bots_friends_set))
            message_to_private_sender = MessageToPrivateSender.MessageToPrivateSender(
                api,
                conn,
                cur,
                users_list,
                vk_sender
            )
            print(users_list)
            messages_object = InviteMessagesToLoyalGroupUsers.objects.all()
            message_to_private_sender.send_invite_messages_to_loyal_user_group(
                [m_object.message for m_object in messages_object]
            )
            # sleep(30)

            multitext_list = [messages_object.message for messages_object in messages_object]
            print(len(multitext_list))
            count_messages_before_ending_work = 1
            # users_set = {VkGroupUserUnion2.objects.get(last_name='Гришаев', first_name='Алексей'), }

            message_to_private_sender.send_invite_messages()

            context['status_of_sending_private_messages'] = \
                send_messages_to_aim_group_user_form.status_of_sending_privat_messages


def like_aim_group_wall_post_through_fake_browser(request):
    print(request.method)

    logger.info(request)
    context = {}
    if request.method == 'POST':
        like_aim_group_user_post_form = LikeAimGroupPostsForm(request.POST)
        if like_aim_group_user_post_form.is_valid():
            logger.info(
                "{}: процесс лайканья постов целевой группы начат".format(datetime.now())
            )
            # group_id = like_aim_group_user_post_form.cleaned_data.get('owner_id')
            post_id = like_aim_group_user_post_form.cleaned_data.get('vk_wall_post_id')
            logger.info("{}: обработали форму, {}".format(
                    datetime.now(),
                    like_aim_group_user_post_form))

            if like_aim_group_user_post_form.cleaned_data.get('is_multiprocessing'):
                raise RuntimeError("Лайки в мультипроцесссинге не реализованы")
            else:
                _make_likes_thgrough_fake_browser(49887978, post_id)

            context['status_of_like_aim_group_user_post'] = \
                like_aim_group_user_post_form.status_of_sending_privat_messages
    # return render(request, )


def _make_likes_thgrough_fake_browser(group_id, wall_post_id, start_sender_id=0):
    bots_senders = BotsSenders.objects.order_by("id").filter(id__gt=start_sender_id)

    for bot in bots_senders:
        # todo грязный хак
        if not bot.is_blocked and bot.id >= start_sender_id:  # 0 < bot.id < 52:  # > bot.id >= 38:
            try:
                # todo возможно следует хранить api-объект пользователя??
                logger.info('открываем браузер для бота: {}'.format(bot))
                print('открываем браузер для бота: {}'.format(bot))
                selenium_sender = SeleniumSender(bot)
                like = False
                while not like:

                        # message_index = random.randint(0, len(multitext_list) - 1)
                        # recipient = users_set.pop()
                        # logger_for_communicator.info(
                        #     "message_index:{}; recipient_first_name: {}; recipient_last_name: {}".format(
                        #         message_index,
                        #         recipient.first_name,
                        #         recipient.last_name
                        #     )
                        # )

                        # message_to_send = multitext_list[message_index].format(recipient.first_name)
                        # logger_for_communicator.info("Сообщение для отправки: {}".format(message_to_send))
                        # # logger_for_communicator.info("message_index:{}".format(message_index))

                    selenium_sender.open_group_page_and_like_wall_post(
                        group_id,
                        wall_post_id
                    )

                    like = True

            except NoSuchElementException as n_ex:
                logger.info(
                    "No such element exceptions caught: {}, {}".format(group_id, n_ex))
                print("No such element exceptions caught: {}, {}".format(group_id, n_ex))
            except WebDriverException as w_ex:
                logger.info("WebDriverException caught: {}, {}".format(group_id, w_ex))
                print("WebDriverException caught: {}, {}".format(group_id, w_ex))


def make_distribution_to_aim_group_users(request):
    logger.info(request)
    context = {}
    if request.method == 'POST':
        logger.info(
            "Рассылка по личкам пользователей дружественной группы в мультипроцессорном режиме".format(datetime.now())
        )
        send_messages_to_aim_group_user_form = SendMessagesToAimGroupUserForm(request.POST)
        if send_messages_to_aim_group_user_form.is_valid():
            logger.info("{}: обработали форму, {}".format({}, send_messages_to_aim_group_user_form))

            # выдёргиваем подписчиков из бд
            users_set = set(GorkiyGroupUser.objects
                            .filter(have_sent_invite_private_message=None)
                            .exclude(can_write_private_message=0))
            bots_friends_set = set(BotsFriends.objects.all())
            users_list = list(users_set.difference(bots_friends_set))

            multitext_list = [messages_object.message
                              for messages_object in
                              InviteMessagesToLoyalGroupUsers.objects.all()]

            print(len(multitext_list))
            count_messages_before_ending_work = 1
            # users_set = {VkGroupUserUnion2.objects.get(last_name='Гришаев', first_name='Алексей'), }

            if send_messages_to_aim_group_user_form.cleaned_data.get('is_multiprocessing'):
                _multiprocessor_send_message_to_private_through_fake_browser(
                    multitext_list,
                    users_list,
                    send_messages_to_aim_group_user_form.cleaned_data.get('start_sender_id')
                )
            else:
                _send_message_to_private_through_fake_browser(
                    multitext_list,
                    users_list,
                    send_messages_to_aim_group_user_form.cleaned_data.get('start_sender_id')
                )

            context['status_of_sending_private_messages'] = \
                send_messages_to_aim_group_user_form.status_of_sending_privat_messages

            return render(context, 'VKSpam_djg/distr_to_privat.html', send_messages_to_aim_group_user_form)


def captcha_input_form(request):
    context = {}
    if request.method == 'POST':
        enter_captcha_form = EnterCaptchaForm(request.POST)
        if enter_captcha_form.is_valid():

            inputed_captcha = enter_captcha_form.cleaned_data.get('inputed_captcha')
            kind_of_distribution = enter_captcha_form.cleaned_data.get('kind_of_distribution')
            print('ввели капчу', inputed_captcha)
            if kind_of_distribution is False:
                sock = socket.socket()
                sock.connect(('localhost', 9092))
            elif kind_of_distribution is True:
                sock = socket.socket()
                sock.connect(('localhost', 9093))
            else:
                # по умолчанию
                sock = socket.socket()

            print("посылаем send из ветки enter_captcha")
            sock.send(b'catch_exception')
            response_data = sock.recv(1024)
            if response_data == b'handling_exception':
                print("ЗДЕЕЕЕЕСЬ ОТСЫЛАЕТСЯ ОТСЫЛАТЬСЯ КАПЧА!!")
                inputed_captcha_encode_to_send = bytes(inputed_captcha, encoding='utf8')
                sock.send(inputed_captcha_encode_to_send)
                # добавляем в контекст переменную
                context['captcha_inf']=enter_captcha_form.captcha_inf.format(inputed_captcha)
                response_data = sock.recv(1024)
                response_data = response_data.decode('utf8')
                print(response_data)
                if response_data == 'end':
                    context['status_for_finish_of_posting_ava_comment'] = \
                        DoCommentPhotoForm.status_for_finish_of_posting_ava_comment
                if response_data == 'end_wall_posting':
                    context['status_for_finish_of_wall_post'] = DoWallPostForm.status_for_finish_of_wall_post

    enter_captcha_form = EnterCaptchaForm()
    context['enter_captcha_form'] = enter_captcha_form
    # return redirect(distr_to_avas)
    return render(request, 'VKSpam_djg/distr_to_avas.html', context)


def bots_senders_params(request):

    if request.method == 'POST':
        AutorisationForm(request.POST)
        result = request.POST.get('autorisation')
        print(result)
        bot = BotsSenders.objects.get(id=result)
        print('{} - авторизуемся под пользователем'.format(datetime.now(), bot))
        logger.info("{} - авторизуемся под пользователем {}".format(datetime.now(), bot))
        autentification_in_vk_via_web_dr(bot.vk_login, bot.vk_password, activity_time=300)

    autorisation_form = AutorisationForm()
    bots_senders = BotsSenders.objects.all()
    context = {'bots_senders': bots_senders,
               'autorisation_form': autorisation_form
               }
    return render(request, 'VKSpam_djg/sender_bots.html', context)


def window_for_captcha(request):
    if request.method == 'POST':
        pass
    enter_captcha_form = EnterCaptchaForm()


def get_ava_comment_text(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CampParamsForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CampParamsForm()

    return render(request, ' VKSpam_djg/detail.html', {'form': form})


def get_set_of_tokens(request, *args):
    """
    Получаем множество токенов для всех польователей, которые не заблокированы
    :param request: http-запрос от django
    :param args:
    :return:
    """
    context = {}
    if request.method == 'POST':
        get_set_of_tokens_form = GetSetOfTokensForm(request.POST)
        if get_set_of_tokens_form.is_valid():
            vk_app_list = VKApplications.objects.all()
            bots = BotsSenders.objects.all().order_by('id')
            for bot in bots:
                # if isinstance(bot.vk_token_expired, None):
                # bot.vk_token_expired = datetime.now()-datetime.day()
                if not bot.is_blocked:  # and bot.vk_token_expired < datetime.now()-datetime.time():
                    print("{} - getting_api_params_for_bot: {} {}.".format(datetime.now(), bot.surname, bot.name))
                    logger.info("{} - getting_api_params_for_bot: {} {}.".format(datetime.now(), bot.surname, bot.name))
                    redirected_url = get_token_by_inner_driver(bot.vk_login, bot.vk_password, vk_app_list=vk_app_list)
                    token, vk_user_id, vk_token_expired = parse_and_save_auth_params(redirected_url)
                    # print(vk_token_expired)
                    bot.vk_token = token
                    # bot.vk_token_expired = vk_token_expired
                    bot.save()
            context['finish_of_getting_tokens'] = get_set_of_tokens_form.finish_of_getting_tokens

    get_set_of_tokens_form = GetSetOfTokensForm()
    context['get_set_of_tokens_form'] = get_set_of_tokens_form
    return render(request, 'VKSpam_djg/sender_bots.html', context)


def add_bots_to_eachother_friends(request, *args):
    context = {}
    if request.method == 'POST':
        add_bots_in_each_other_friend_form = AddBotsInEachOtherFriendForm(request.POST)
        if add_bots_in_each_other_friend_form.is_valid():
            bots = BotsSenders.objects.all().filter(is_blocked=False)
            print(bots)
            apis = get_bots_and_apis()
            p_conn, p_cur = connection_to_postgres()
            add_bots_to_friends_of_each_other(p_conn, p_cur, apis, bots)

    add_bots_in_each_other_friend_form = AddBotsInEachOtherFriendForm()
    context['add_bots_in_each_other_friend_form'] = add_bots_in_each_other_friend_form
    return render(request, 'VKSpam_djg/sender_bots.html', context)


def get_aim_group_wall_posts(request):
    context = {}
    if request.method == 'POST':
        get_aim_group_wall_posts = GetAimGroupWallPostsForm(request.POST)

        api, postgres_con, postgres_cur = get_important_params()
        posts = get_wall_posts(api)
        for post in posts['items']:
            vk_wall_post = VkWallPosts()
            print(post['owner_id'])
            vk_wall_post.owner_id = post['owner_id']
            print(post['id'])
            vk_wall_post.vk_wall_post_id = post['id']
            vk_wall_post.vk_json_post_parameters = post
            vk_wall_post.save()
        context['status_for_get_aim_group_wall_posts'] = posts
        return render(request, 'VKSpam_djg/working_with_aim_group.html', context)


def working_with_aim_group(request, *args):
    context = {}
    if request.method == 'POST':
        get_updates_of_aim_group = GetUpdatesOfAimGroupForm(request.POST)
        if get_updates_of_aim_group.is_valid():
            api, postgres_con, postgres_cur = get_important_params()
            result_of_update = final_getting_subscribers_with_offsets_loop(
                api,
                group_id='gorkyvery',
                insert_to_aim_group=True)
            if result_of_update == 'OK':
                context['status_for_getting_subscribers_of_aim_group'] = \
                    'добавление новых пользователей в целевую группу закончено'
                print(result_of_update)
                return render(request, 'VKSpam_djg/working_with_aim_group.html', context)
            else:
                raise RuntimeError("Не удалось добавить новых пользователей в целевую группу")

    get_updates_of_aim_group = GetUpdatesOfAimGroupForm()
    get_aim_group_wall_posts = GetAimGroupWallPostsForm()
    like_aim_group_posts_form = LikeAimGroupPostsForm()
    context['get_updates_of_aim_group'] = get_updates_of_aim_group
    context['get_aim_group_wall_posts'] = get_aim_group_wall_posts
    context['like_aim_group_posts_form'] = like_aim_group_posts_form
    return render(request, 'VKSpam_djg/working_with_aim_group.html', context)


#         process = Process(
#             target=_multiproc_send_in_private_trough_fake_browser,
#             args=(bot, users_set, multitext_list))
#         selenium_sending_processes.append(process)
#
# multiproc_index = 0
# for process in selenium_sending_processes:
#     process.start()
#     if multiproc_index is 5:
#         while selenium_sending_processes[multiproc_index].is_alive:
#             sleep(10)
#     multiproc_index += 1

# for bot in BotsSenders.objects.order_by("id"):
#     # todo грязный хак
#     if not bot.is_blocked and bot.id >= 0:  # 0 < bot.id < 52:  # > bot.id >= 38:
#
#         try:
#             # todo возможно следует хранить api-объект пользователя??
#             logger_for_communicator.info('открываем браузер для бота: {}'.format(bot))
#             print('открываем браузер для бота: {}'.format(bot))
#             selenium_sender = SeleniumSender(bot)
#             sent = False
#
#             while not sent:
#                 try:
#                     message_index = random.randint(0, len(multitext_list) - 1)
#                     recipient = users_set.pop()
#                     print("message_index:{}; recipient_first_name: {}; recipient_last_name: {}"
#                           .format(message_index, recipient.first_name, recipient.last_name))
#
#                     print(multitext_list)
#                     message_to_send = multitext_list[message_index].format(recipient.first_name)
#                     print("Сообщение для отправки: {}".format(message_to_send))
#                     logger_for_communicator.info("message_index:{}".format(message_index))
#
#                     selenium_sender.open_page_and_write_message(
#                         recipient.vk_id,
#                         message_to_send
#                     )
#
#                     recipient.have_sent_invite_private_message = True
#                     recipient.save()
#
#                     sleep(1)
#                     bot.day_sent_message_count = 1
#                     sent = True
#                 except TooFarLastAutorisationException:
#                     logger_for_communicator.info("to far last autorisation from recipient: {}".format(recipient))
#                     recipient.can_write_private_message = False
#                     recipient.save()
#                 except elementNotVisibleException:
#                     recipient.can_write_private_message = False
#                     recipient.save()
#                     logger_for_communicator.info("can't write message to recipient: {}".format(recipient))
#
#         except NoSuchElementException as n_ex:
#             recipient.can_write_private_message = 0
#             recipient.save()
#             logger_for_communicator.info(
#                 "No such element exceptions caught: {}, {}".format(recipient, n_ex))
#
#         except WebDriverException as w_ex:
#             logger_for_communicator.info("WebDriverException caught: {}, {}".format(recipient, w_ex))

def _mult(bot, multitext_list, recipient):
    if not bot.is_blocked and bot.id >= 0:  # 0 < bot.id < 52:  # > bot.id >= 38:
        try:
            # todo возможно следует хранить api-объект пользователя??
            logger.info('открываем браузер для бота: {}'.format(bot))
            print('открываем браузер для бота: {}'.format(bot))
            selenium_sender = SeleniumSender(bot)
            try:
                message_index = random.randint(0, len(multitext_list) - 1)
                logger.info(
                    "message_index:{}; recipient_first_name: {}; recipient_last_name: {}".format(
                        message_index,
                        recipient.first_name,
                        recipient.last_name
                    )
                )

                message_to_send = multitext_list[message_index].format(recipient.first_name)
                logger.info("Сообщение для отправки: {}".format(message_to_send))
                # logger_for_communicator.info("message_index:{}".format(message_index))

                selenium_sender.open_page_and_write_message(
                    recipient.vk_id,
                    message_to_send
                )
                # todo грязных хак
                if isinstance(recipient, VkGroupUserUnion2):
                    recipient.have_sent_messages = True
                elif isinstance(recipient, GorkiyGroupUser):
                    recipient.have_sent_invite_private_message = True
                recipient.save()
                bot.day_sent_message_count = 1
                # bot.save()
            except TooFarLastAutorisationException:
                logger.info("to far last autorisation from recipient: {}".format(recipient))
                recipient.can_write_private_message = False
                recipient.save()
            except elementNotVisibleException:
                recipient.can_write_private_message = False
                recipient.save()
                logger.info("can't write message to recipient: {}".format(recipient))

        except NoSuchElementException as n_ex:
            logger.info("No such element exceptions caught: {}, {}".format(recipient, n_ex))

        except WebDriverException as w_ex:
            logger.info("WebDriverException caught: {}, {}".format(recipient, w_ex))


def _multiprocessor_send_message_to_private_through_fake_browser(multitext_list, users_set, start_sender_id):
    bots_senders = BotsSenders.objects.order_by("id").filter(id__gt=start_sender_id)

    processes = []
    for bot in bots_senders:  # BotsSenders.objects.order_by("id"):
        if len(processes) < 5:
            from django.db import connection
            connection.close()

            process = Process(target=_mult, args=(bot, multitext_list, users_set.pop()))
            processes.append(process)
            process.start()

    for process in processes:
        process.join()

    print(processes)
    # sleep(600)


def _send_message_to_private_through_fake_browser(multitext_list, users_set, start_sender_id):
    bots_senders = BotsSenders.objects.order_by("id").filter(id__gt=start_sender_id)

    for bot in bots_senders:
        # todo грязный хак
        if not bot.is_blocked and bot.id >= start_sender_id:  # 0 < bot.id < 52:  # > bot.id >= 38:
            try:
                # todo возможно следует хранить api-объект пользователя??
                logger.info('открываем браузер для бота: {}'.format(bot))
                print('открываем браузер для бота: {}'.format(bot))
                selenium_sender = SeleniumSender(bot)
                sent = False
                while not sent:
                    try:
                        message_index = random.randint(0, len(multitext_list) - 1)
                        recipient = users_set.pop()
                        logger.info(
                            "message_index:{}; recipient_first_name: {}; recipient_last_name: {}".format(
                                message_index,
                                recipient.first_name,
                                recipient.last_name
                            )
                        )
        
                        message_to_send = multitext_list[message_index].format(recipient.first_name)
                        logger.info("Сообщение для отправки: {}".format(message_to_send))
                        # logger_for_communicator.info("message_index:{}".format(message_index))
        
                        selenium_sender.open_page_and_write_message(
                            recipient.vk_id,
                            message_to_send
                        )
                        # todo грязных хак
                        if isinstance(recipient, VkGroupUserUnion2):
                            recipient.have_sent_messages = True
                        elif isinstance(recipient, GorkiyGroupUser):
                            recipient.have_sent_invite_private_message = True
                        recipient.save()
                        bot.day_sent_message_count = 1
                        sent = True
                    except TooFarLastAutorisationException:
                        logger.info("to far last autorisation from recipient: {}".format(recipient))
                        recipient.can_write_private_message = False
                        recipient.save()
                    except elementNotVisibleException:
                        recipient.can_write_private_message = False
                        recipient.save()
                        logger.info("can't write message to recipient: {}".format(recipient))
        
            except NoSuchElementException as n_ex:
                logger.info(
                    "No such element exceptions caught: {}, {}".format(recipient, n_ex))
        
            except WebDriverException as w_ex:
                logger.info("WebDriverException caught: {}, {}".format(recipient, w_ex))


def make_distribution_in_privat_through_fake_browser(request, *args):
    context = {}
    if request.method == 'POST':
        make_distribution_through_fake_browser_form = MakeDistributionThroughFakeBrowserForm(request.POST)
        # ветка для отправки в личку посредством фейкового браузера
        if make_distribution_through_fake_browser_form.is_valid():

            logger.info('Отправка посредством фейкового браузера')

            vk_group_id_for_privat_msg = \
                make_distribution_through_fake_browser_form.cleaned_data.get('vk_group_id_multisender')

            logger.info('стартует отправка пользователям группы:{}'.format(vk_group_id_for_privat_msg))
            print('стартует отправка пользователям группы:{}'.format(vk_group_id_for_privat_msg))

            multtext_list = [obj.message for obj in PrivateMessages.objects.all()]
            print(type(multitext_list))
            print(len(multitext_list))
            count_messages_before_ending_work = 1

            # выдёргиваем подписчиков из бд
            users_set = set(VkGroupUserUnion2.objects
                            .filter(vk_group_id=vk_group_id_for_privat_msg)
                            .exclude(have_sent_messages=True)
                            .exclude(have_post_photo_comment=True)
                            .exclude(can_write_private_message=0))

            _send_message_to_private_through_fake_browser(
                multitext_list,
                users_set,
                make_distribution_through_fake_browser_form.cleaned_data.get('start_sender_id')
            )

            # users_set = {VkGroupUserUnion2.objects.get(last_name='Гришаев', first_name='Алексей'), }
            # selenium_sending_processes = []
            #         process = Process(
            #             target=_multiproc_send_in_private_trough_fake_browser,
            #             args=(bot, users_set, multitext_list))
            #         selenium_sending_processes.append(process)
            #
            # multiproc_index = 0
            # for process in selenium_sending_processes:
            #     process.start()
            #     if multiproc_index is 5:
            #         while selenium_sending_processes[multiproc_index].is_alive:
            #             sleep(10)
            #     multiproc_index += 1
            # for process in selenium_sending_processes:
            #     while process.is_alive:
            #         sleep(1)
            #         continue
            #
            # for user in users_set:
            #     user.save()

    return render(request, 'VKSpam_djg/distr_to_privat.html', context)


def make_likes(request):
    context = {}
    if request.method == 'POST':
        get_aim_group_wall_posts_form = GetAimGroupWallPostsForm(request.POST)
        if get_aim_group_wall_posts_form.is_valid():

            # api, postgres_con, postgres_cur = get_important_params()
            # result_of_update = final_getting_subscribers_with_offsets_loop(
            #     api,
            #     group_id='gorkyvery',
            #     insert_to_aim_group=True)
            # if result_of_update == 'OK':
            #     context['status_for_getting_subscribers_of_aim_group'] = \
            #         'добавление новых абонентов в целевую группу закончено'
            #     print(result_of_update)
                return render(request, 'VKSpam_djg/working_with_aim_group.html', context)

    get_aim_group_wall_posts_form = GetAimGroupWallPostsForm()
    context['get_updates_of_aim_group'] = get_aim_group_wall_posts_form
    return render(request, 'VKSpam_djg/working_with_aim_group.html', context)


def _multiproc_send_in_private_trough_fake_browser(bot, users_set, multitext_list):
    try:
        # todo возможно следует хранить api-объект пользователя??
        logger.info('открываем браузер для бота: {}'.format(bot))
        print('открываем браузер для бота: {}'.format(bot))
        selenium_sender = SeleniumSender(bot)
        sent = False

        while not sent:
            try:
                message_index = random.randint(0, len(multitext_list) - 1)
                recipient = users_set.pop()
                print("message_index:{}; recipient_first_name: {}; recipient_last_name: {}"
                      .format(message_index, recipient.first_name, recipient.last_name))

                print(multitext_list)
                message_to_send = multitext_list[message_index].format(recipient.first_name)
                print("Сообщение для отправки: {}".format(message_to_send))
                logger.info("message_index:{}".format(message_index))

                selenium_sender.open_page_and_write_message(
                    recipient.vk_id,
                    message_to_send
                )

                recipient.have_sent_messages = True
                # recipient.save()
                bot.day_sent_message_count = 1
                sent = True
            except TooFarLastAutorisationException:
                logger.info("to far last autorisation from recipient: {}".format(recipient))
                recipient.can_write_private_message = False
                recipient.save()
            except elementNotVisibleException:
                recipient.can_write_private_message = False
                recipient.save()
                logger.info("can't write message to recipient: {}".format(recipient))

    except NoSuchElementException as n_ex:
        logger.info(
            "No such element exceptions caught: {}, {}".format(recipient, n_ex))

    except WebDriverException as w_ex:
        logger.info("WebDriverException caught: {}, {}".format(recipient, w_ex))


def get_notifications_for_sender_bots_and_sent_to_telegram(request):
    context = {}
    if request.method == 'POST':
        bot_senders = BotsSenders.objects.order_by("id")
        telegram_bot = TelegramBot()
        for bot in bot_senders:
            vk_notifications = VkNotifications(bot)
            all_mentions = vk_notifications.get_all_mentions()
            if all_mentions['count'] > 0:
                logger.info("{} -for bot {} got all recent mentions".format(datetime.now(), bot))
                for mention in all_mentions['items']:
                    logger.info("{} - for bot '{}', parent:{}; feedback: {}".
                                format(datetime.now(), bot, mention['parent']['text'], mention['feedback']['text']))
                    telegram_bot.send_message("Bot: {}. Message: {}. Feedback: {}"
                                              .format(bot, mention['parent']['text'], mention['feedback']['text']))
                sleep(300)
            else:
                logger.info("{} - for bot {} there are no mentions".format(datetime.now(), bot))
        return render(request, "", context)


'''
def create_camp(request, *args):
    context = {}
    if request.method == 'POST':
     '''
'''
def start_campaign(request, *args):
    context = {}
    if request.method == 'POST':
        start_campaign_form = StartCampaignForm(request.POST)
        if start_campaign_form.is_valid():
            camp_id = start_campaign_form.cleaned_data.get['camp_id']
            camp_id =  CampParams.objects.get(id=id)

    #context = campaign_list
    return render(request, 'VKSpam_djg/set_up_campaigns.html')
'''