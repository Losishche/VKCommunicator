#!/usr/bin/env python3

from django.shortcuts import render,  HttpResponseRedirect, render_to_response
from django.template import Context, loader
from django.http import HttpResponse
import logging
import json
from multiprocessing import Process, Queue
from .forms import NameForm
from .forms import CampParamsForm
from .forms import UploadFileForm
#from .forms import GetCampaignIdForInserterForm
from .forms import DoCommentPhotoForm
from .forms import GetTokenForm
from .forms import AskTokenForm
from .forms import EnterGroupIdForm
from .forms import EnterCaptchaForm
from .forms import DoPrivatMessageForm
from .forms import GetStatisticsForm
from .forms import DoWallPostForm, GetAvaInfoAndPhotoSettingsForm, GetSetOfTokensForm, Autorisation_Form, DoPrivatMultisenderSendingMessForm
from .forms import MultisenderGetAvaInfoAndPhotoSettingForm
import sys
import socket
# добавляем путь, где находится backend с бизнес-логикой
sys.path.append('/home/grishaev/PycharmProjects/VKSpammer/')
from time import sleep
from app_info import get_subscriber_settings_with_multisender_and_multiproc
from app_info import parse_and_save_auth_params
from app_info import  get_token_by_inner_driver, get_auth_params_from_interface, autentification_in_vk_via_web_dr
from app_info import final_sending_privat_message, get_ava_id_and_insert_in_into_db, get_settings_of_photo, do_comment_photo, many_posts_wall_message
from app_info import final_getting_subscribers_with_offsets_loop
from app_info import get_important_params
from app_info import logger_for_communicator, proccess_log_file_path
from app_info import attachments #todo временное
from work_with_DB import select_count_have_posted_ava_messages
from work_with_DB import connection_to_postgres
from .models import VkGroupUserUnion, BotsSenders, CampParams, AvaMessages
from django.db.models import  Min
#from app_info import do_comment_photo

#import  inner_server

'''
proccess_log_file_path = '/home/grishaev/PycharmProjects/VKSpammer/VKSpammer/VKSpam_djg/static/VKSpam_djg/process_log.txt'
logger_for_communicator = logging.getLogger('logger_for_communicator')
logger_for_communicator.setLevel(logging.INFO)
fh = logging.FileHandler(proccess_log_file_path)
fh.setLevel(logging.INFO)
logger_for_communicator.addHandler(fh)
'''

#logging.basicConfig(level=logging.INFO)

'''
def index(request):

    t = loader.get_template('VKSpam_djg/index.html')
    c = Context({
        'list': [1,2,3,4],
    })
    return HttpResponse(t.render(c))
'''

def index(request):
    context = {}
    if request.method == 'POST':
        logging.info('обработали запрос')
        # create a form instance and populate it with data from the request:
        #form = CampParamsForm(request.POST)
        get_token_form = GetTokenForm(request.POST)
        ask_token_form = AskTokenForm(request.POST)
        enter_group_id_form = EnterGroupIdForm(request.POST)
        do_comment_photo_form = DoCommentPhotoForm(request.POST)
        enter_captcha_form = EnterCaptchaForm(request.POST)
        do_wall_post_form = DoWallPostForm(request.POST)
        do_privat_message_form = DoPrivatMessageForm(request.POST)

        #logging.info(get_token_form.is_valid())
        #logging.info(ask_token_form.is_valid())
        res = request.POST
        print(res)
        if get_token_form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            user_token = get_token_form.cleaned_data.get('user_token')
            parsed_token, vk_user_id = parse_and_save_auth_params(user_token)
            try:
                sender = BotsSenders.objects.get(vk_user_id=vk_user_id)
            except BotsSenders.DoesNotExist:
                sender = False
            if sender:
                sender.vk_token = parsed_token
                sender.save()

            result_of_hangling_token_string = "Токен успешно загружен в программу " + parsed_token
            logging.info('обработали полученный токен')
            context['result_of_hangling_token_string'] = result_of_hangling_token_string
            #return HttpResponseRedirect('/thanks/')
        #elif request.POST.get('ask_token_btn'): хз, но почему-то изменилось ПОСЛЕ ДОБАВЛЕНИЯ CSS((
            #result = request.POST.get('ask_token_btn')#

        elif request.POST.get('take_token'):
            result = request.POST.get('take_token')
            logging.info(result)
            if result != False: #сознательное дублирование изначального условия
                get_auth_params_from_interface()

        elif request.POST.get('take_all_token_automatically'):
            result = request.POST.get('take_all_token_automatically')
            for bot in BotsSenders.objects.all():
                get_token_by_inner_driver(bot.vk_login, bot.vk_password)

        elif enter_group_id_form.is_valid():
            group_id_to_insert= enter_group_id_form.cleaned_data.get('inputed_group_id')
            logging.info(group_id_to_insert)
            api, conn, cur = get_important_params()
            result = final_getting_subscribers_with_offsets_loop(api, group_id_to_insert)
            if result == 'OK':
                context['status_for_getting_subscribers'] = enter_group_id_form.status_for_getting_subscribers.format(group_id_to_insert)

        elif do_comment_photo_form.is_valid(): #чтобы работать с формой, нужно выполнить ф-ю is_valid!!!
            vk_group_id  = do_comment_photo_form.cleaned_data.get('vk_group_id') # потому что словарь!
            message = do_comment_photo_form.cleaned_data['message'] #потому что словарь!
            #message = do_comment_photo_form.message
            print('тут что-то происходит, а не должно при нажатии кнопки загрузить', vk_group_id, message)
            #api, postgres_con, postgres_cur = get_important_params()
            #generator_for_commenting = do_comment_photo(api, postgres_con, postgres_cur, vk_group_id, consider_user_sex=True, is_run_from_interface=True)
            #todo костыльные внутренние серверы блин

            sock = socket.socket()
            sock.connect(('localhost', 9092))
            #sock.send(b'start_generator')
            #data = sock.recv(10244)
            open_signal = bytes('start_commenting_photo', encoding='utf8')
            #print(message)
            sock.send(open_signal)
            data = sock.recv(1024)
            if data == b'start_commenting_photo_resp':
                parameters = vk_group_id + ', ' + message
                parameters = bytes(parameters, encoding='utf8')
                sock.send(parameters)
                context['status_for_start_of_posting_ava_comment'] = do_comment_photo_form.status_for_start_of_posting_ava_comment
                data = sock.recv(1024)
                if data == b'cought_exeption':
                    context['status_for_cought_exeption'] = '!!!!'

            print(data)
            if data == 'end':
                #sock.close()
                context['status_for_finish_of_posting_ava_comment'] = do_comment_photo_form.status_for_finish_of_posting_ava_comment
            elif data =='unknown_parameter':
                sock.close()

            '''for gen_result in generator_for_commenting:
                if gen_result == 'handling_exception':
                    #todo всплывающее окно нужно ли всплывающее окно???
                    inputed_captcha = input()
                    print('принята капча', inputed_captcha)
                    generator_for_commenting.send(inputed_captcha)
            '''
        elif do_wall_post_form.is_valid():
            #ветка для постов на стенку
            vk_group_id_for_wall_post  = do_wall_post_form.cleaned_data.get('vk_group_id_for_wall_post') # потому что словарь!
            wall_post = do_wall_post_form.cleaned_data['wall_post'] #потому что словарь!

            #context['vk_group_id_for_wall_post'] = vk_group_id_for_wall_post
            #context['wall_post'] = wall_post
            #todo подумать на счёт портов
            sock = socket.socket()
            sock.connect(('localhost', 9093))
            open_signal = bytes('start_posting_wall_comments', encoding='utf8')
            #print(message)
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
                #sock.close()
                context['status_for_finish_of_wall_post'] = do_wall_post_form.status_for_finish_of_wall_post
            elif data =='unknown_parameter':
                sock.close()

        elif  enter_captcha_form.is_valid():

            inputed_captcha = enter_captcha_form.cleaned_data.get('inputed_captcha')
            kind_of_distribution = enter_captcha_form.cleaned_data.get('kind_of_distribution')
            print('ввели капчу', inputed_captcha)
            if kind_of_distribution == False:
                sock = socket.socket()
                sock.connect(('localhost', 9092))
            elif kind_of_distribution == True:
                sock = socket.socket()
                sock.connect(('localhost', 9093))
            else:
                #по умолчанию
                sock = socket.socket()

            print("посылаем send из ветки enter_captcha")
            sock.send(b'catch_exception')
            response_data = sock.recv(1024)
            if response_data == b'handling_exception':
                print("ЗДЕЕЕЕЕСЬ ОТСЫЛАЕТСЯ ОТСЫЛАТЬСЯ КАПЧА!!")
                inputed_captcha_encode_to_send = bytes(inputed_captcha, encoding='utf8')
                sock.send(inputed_captcha_encode_to_send)
                #добавляем в контекст переменную
                context['captcha_inf']=enter_captcha_form.captcha_inf.format(inputed_captcha)
                response_data = sock.recv(1024)
                response_data = response_data.decode('utf8')
                print(response_data)
                if response_data == 'end':
                     context['status_for_finish_of_posting_ava_comment'] = do_comment_photo_form.status_for_finish_of_posting_ava_comment
                if response_data == 'end_wall_posting':
                     context['status_for_finish_of_wall_post'] = do_wall_post_form.status_for_finish_of_wall_post

        elif do_privat_message_form.is_valid():
            vk_group_id_2  = do_privat_message_form.cleaned_data.get('vk_group_id_2')
            privat_message = do_privat_message_form.cleaned_data['privat_message']
            api, conn, cur = get_important_params()
            print(vk_group_id_2)
            res = final_sending_privat_message(api, conn, cur, vk_group_id_2)

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
    #form_for_subscribed_statistic = GetMessageTextForm()
    context['ask_token_form'] = ask_token_form
    context['form_to_get_user_token'] = form_to_get_user_token
    context['enter_group_id_form'] = enter_group_id_form
    context['do_comment_photo_form'] = do_comment_photo_form
    context['enter_captcha_form'] = enter_captcha_form
    context['do_wall_post_form'] = do_wall_post_form
    context['do_privat_message_form'] =  do_privat_message_form

    return render(request, 'VKSpam_djg/index.html', context) #передаем ЗАПРОС, ШАБЛОН и КОНТЕКСТ (словарь переменных с объектами)

    #функция render() первым аргументом принимает объект запроса, также название шаблона и необязательный словарь значений контекста.
    ## Возвращает объект HttpResponse содержащий выполненный шаблон с указанным контексто

def statistics(request, group_id=None):

    context = {}
    if request.method == 'POST':
        print('отладка')
        get_statistics_form = GetStatisticsForm(request.POST)
        if get_statistics_form.is_valid():
            #print('отладка2')
            choice_id = get_statistics_form.cleaned_data.get('CHOICES_FOR_KIND_OF_SENDING')
            print(choice_id)
            group_id = get_statistics_form.cleaned_data.get('vk_group_id_3')
            context['group_id'] = group_id
            if choice_id == '1':
                print('отладка 2')
                #postgres_con, postgres_cur =
                #select_count_have_posted_ava_messages(postgres_con, postgres_cur, group_id=group_id)
                count_of_photo_comment_posted = VkGroupUserUnion.objects.filter(vk_group_id=group_id, have_post_photo_comment=True).count()
                context['count_of_photo_comment_posted'] = count_of_photo_comment_posted

            elif choice_id == '2':
                #postgres_con, postgres_cur =
                #select_count_have_posted_ava_messages(postgres_con, postgres_cur, group_id=group_id)
                count_of_privat_message_sent= VkGroupUserUnion.objects.filter(vk_group_id=group_id, have_sent_messages=1).count()
                context['count_of_privat_message_sent']= count_of_privat_message_sent

            elif choice_id == '3':
                count_of_group_subscribers = VkGroupUserUnion.objects.filter(vk_group_id=group_id).count()
                print(count_of_group_subscribers)
                context['count_of_group_subscribers']= count_of_group_subscribers

            elif choice_id == '4':
                count_of_photo_comment_posted = VkGroupUserUnion.objects.filter(vk_group_id=group_id, have_post_photo_comment=True).count()
                context['count_of_photo_comment_posted'] = count_of_photo_comment_posted
                count_of_privat_message_sent= VkGroupUserUnion.objects.filter(vk_group_id=group_id, have_sent_messages=1).count()
                context['count_of_privat_message_sent']= count_of_privat_message_sent
                count_of_wall_post_sent = VkGroupUserUnion.objects.filter(vk_group_id=group_id, have_post_wall_comment=True).count()
                context['count_of_wall_post_sent']= count_of_wall_post_sent
                count_of_group_subscribers = VkGroupUserUnion.objects.filter(vk_group_id=group_id).count()
                context['count_of_group_subscribers']= count_of_group_subscribers
                count_of_possible_ava_comment = VkGroupUserUnion.objects.filter(vk_group_id=group_id, can_post_ava_comment=True).count()
                context['count_of_possible_ava_comment']= count_of_possible_ava_comment
                count_of_possible_privat_message = VkGroupUserUnion.objects.filter(vk_group_id=group_id, can_write_private_message=1).count()
                context['count_of_possible_privat_message']= count_of_possible_privat_message
                #count_of_all_sent_messages_and_posts = VkGroupUserUnion.objects.filter(
                #    vk_group_id=group_id,
                #    have_post_ava_comment=1).count()
                #context['count_of_all_sent_messages_and_posts'] = count_of_all_sent_messages_and_posts

    get_statistics_form = GetStatisticsForm()
    context['get_statistics_form'] = get_statistics_form
    return  render(request, 'VKSpam_djg/statistics.html', context)


def distr_to_avas(request):
    context = {}
    with open(proccess_log_file_path, 'w') as f: pass
    temp_stdout = sys.stdout
    #sys.stdout = open(proccess_log_file_path, 'w')
    if request.method == 'POST':
        logger_for_communicator.info('обработали запрос')
        # create a form instance and populate it with data from the request:
        do_comment_photo_form = DoCommentPhotoForm(request.POST)
        enter_captcha_form = EnterCaptchaForm(request.POST)
        print(do_comment_photo_form.is_valid())
        logger_for_communicator.info('Is form valid? {}'.format(do_comment_photo_form.is_valid()))
        if do_comment_photo_form.is_valid(): #чтобы работать с формой, нужно выполнить ф-ю is_valid!!!
            vk_group_id  = do_comment_photo_form.cleaned_data.get('vk_group_id') # потому что словарь!
            message = do_comment_photo_form.cleaned_data['message'] #потому что словарь!
            is_autocaptcha = do_comment_photo_form.cleaned_data.get('is_autocaptcha')
            is_sex_considered = do_comment_photo_form.cleaned_data.get('is_sex_considered')
            bots_sender = do_comment_photo_form.cleaned_data.get('bots_senders')
            is_multitext = do_comment_photo_form.cleaned_data.get('is_multitext')
            #message = do_comment_photo_form.message
            print('тут что-то происходит', vk_group_id, message, bots_sender)
            #пишет в лог для отображения в интерфейсе
            logger_for_communicator.info('starting work with group: {}, message: \'{}\', sender: {}'.format(vk_group_id, message, bots_sender))
            #api, postgres_con, postgres_cur = get_important_params()
            #generator_for_commenting = do_comment_photo(api, postgres_con, postgres_cur, vk_group_id, consider_user_sex=True, is_run_from_interface=True)
            #todo костыльные внутренние серверы блин

            sock = socket.socket()
            sock.connect(('localhost', 9092))
            print(is_autocaptcha)
            logger_for_communicator.info('автокапча активирована? {}'.format(is_autocaptcha))
            if is_autocaptcha:
                if is_sex_considered:
                    #некоторое почти дублирование кода
                    if bots_sender:
                        user_token = BotsSenders.objects.get(vk_user_id=bots_sender).vk_token
                        #работа напрямую с функцией backend
                        #if BotsSenders.object.get()
                        print('start distr with token', user_token)
                        logger_for_communicator.info('start distr with token: {}'.format(user_token))
                        api, conn, cur = get_important_params(user_token)
                        gen_cp = do_comment_photo(
                            api, conn, cur, vk_group_id, consider_user_sex=True, is_run_from_interface=True, auto_captcha=True)
                             #чёрт знает какая логика!!! тут прямо в функцию, в else - через внут.сервер!!!
                        print("КАКОЙ_ТО ОЧЕНЬ СТРАННЫЙ БАГ", gen_cp)
                        for item in gen_cp:
                            print('iteration_of_gen: {}'.format(item))
                            logger_for_communicator.info('iteration_of_gen: {}'.format(item))
                    else:
                        if is_multitext:
                            api, conn, cur = get_important_params()
                            texts = AvaMessages.objects
                            gen_cp = do_comment_photo(
                                api, conn, cur, vk_group_id,
                                consider_user_sex=True, is_run_from_interface=True, auto_captcha=True, is_multitext=texts
                            )
                                 #чёрт знает какая логика!!! тут прямо в функцию, в else - через внут.сервер!!!
                            for item in gen_cp:
                                print(item)
                                logger_for_communicator.info('user: {}'. format(item))
                        else:
                            api, conn, cur = get_important_params()
                            gen_cp = do_comment_photo(
                                api, conn, cur, vk_group_id,
                                consider_user_sex=True, is_run_from_interface=True, auto_captcha=True
                            )
                                 #чёрт знает какая логика!!! тут прямо в функцию, в else - через внут.сервер!!!
                            for item in gen_cp:
                                print(item)
                                logger_for_communicator.info('user: {}'. format(item))
                else:
                    if bots_sender:
                        user_token = BotsSenders.objects.get(vk_user_id=bots_sender).vk_token
                        #работа напрямую с функцией backend
                        #if BotsSenders.object.get()
                        print('start distr with token', user_token)
                        logger_for_communicator.info('start distr with token: {}'.format(user_token))
                        api, conn, cur = get_important_params(user_token)
                        gen_cp = do_comment_photo(
                            api, conn, cur, vk_group_id, is_run_from_interface=True, auto_captcha=True)
                             #чёрт знает какая логика!!! тут прямо в функцию, в else - через внут.сервер!!!
                        print("КАКОЙ_ТО ОЧЕНЬ СТРАННЫЙ БАГ", gen_cp)
                        for item in gen_cp:
                            print('iteration_of_gen: {}'.format(item))
                            logger_for_communicator.info('iteration_of_gen: {}'.format(item))
                    else:
                        if is_multitext:
                            api, conn, cur = get_important_params()
                            texts = AvaMessages.objects
                            gen_cp = do_comment_photo(
                                api, conn, cur, vk_group_id, is_run_from_interface=True, auto_captcha=True, is_multitext=texts)
                                 #чёрт знает какая логика!!! тут прямо в функцию, в else - через внут.сервер!!!
                            for item in gen_cp:
                                print(item)
                                logger_for_communicator.info('user: {}'. format(item))
                        else:
                            api, conn, cur = get_important_params()
                            gen_cp = do_comment_photo(
                                api, conn, cur, vk_group_id, is_run_from_interface=True, auto_captcha=True)
                                 #чёрт знает какая логика!!! тут прямо в функцию, в else - через внут.сервер!!!
                            for item in gen_cp:
                                print(item)
                                logger_for_communicator.info('user: {}'. format(item))
            else:
                #работа через внутренний сервер!!!!
                open_signal = bytes('start_commenting_photo', encoding='utf8')
                #print(message)
                sock.send(open_signal)
                data = sock.recv(1024)
                if data == b'start_commenting_photo_resp':
                    parameters = vk_group_id + ', ' + message
                    parameters = bytes(parameters, encoding='utf8')
                    sock.send(parameters)
                    context['status_for_start_of_posting_ava_comment'] = do_comment_photo_form.status_for_start_of_posting_ava_comment
                    data = sock.recv(1024)
                    #std_out_messages = open('/home/grishaev/PycharmProjects/VKSpammer/test_stdout')
                    std_out_messages = open('../test_stdout')
                    context['std_out_messages'] = std_out_messages.readline()
                    if data == b'cought_exeption':
                        context['status_for_cought_exeption'] = '!!!!' #что ЭТО такое??


                print(data)
                if data == 'end':
                    #sock.close()
                    context['status_for_finish_of_posting_ava_comment'] = do_comment_photo_form.status_for_finish_of_posting_ava_comment
                elif data =='unknown_parameter':
                    sock.close()

    #конечная ветка
    #sys.stdout.close()
    #sys.stdout = temp_stdout
    do_comment_photo_form = DoCommentPhotoForm()
    enter_captcha_form = EnterCaptchaForm()
    context['do_comment_photo_form'] = do_comment_photo_form
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
            #sleep(300)
            vk_gr_id_for_getting_settings = get_ava_info_and_photo_settings_form.cleaned_data.get('vk_group_id')
            api, postgres_con, postgres_cur = get_important_params()
            result = get_ava_id_and_insert_in_into_db(api, postgres_con, postgres_cur, group_id=vk_gr_id_for_getting_settings)
            result2 = get_settings_of_photo(api, postgres_con, postgres_cur, group_id=vk_gr_id_for_getting_settings)

        elif multisender_get_ava_info_and_photo_setting_form.is_valid():
            vk_gr_id_for_getting_settings = \
                multisender_get_ava_info_and_photo_setting_form.cleaned_data.get('vk_group_id_multisender_g_a_i_a_p_s_f')

            #процессы для мультипроцессинга
            queue = Queue()
            allProcess = []
            offset = 0
            min_value = VkGroupUserUnion.objects.all(vk_group_id=vk_gr_id_for_getting_settings).aggregate(Min('id')) #todoхз, как тут делать
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
                 p.start()


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
            #ветка для постов на стенку
            vk_group_id_for_wall_post  = do_wall_post_form.cleaned_data.get('vk_group_id') # потому что словарь!
            wall_post = do_wall_post_form.cleaned_data['wall_post'] #потому что словарь!
            is_autocaptcha = do_wall_post_form.cleaned_data.get('is_autocaptcha')
            bots_sender = do_wall_post_form.cleaned_data.get('bots_senders')
            print(vk_group_id_for_wall_post, is_autocaptcha)
            if is_autocaptcha:
                if bots_sender:
                    user_token = BotsSenders.objects.get(vk_user_id=bots_sender).vk_token
                    #работа напрямую с функцией backend
                    print('start distr_to_walls with old token', user_token)
                    api, postgres_con, postgres_cur = get_important_params(user_token)
                    #api, postgres_con, postgres_cur = get_important_params()
                    gen_cp = many_posts_wall_message(
                        api, postgres_con, postgres_cur, vk_group_id_for_wall_post, is_run_from_interface=True, auto_captcha=True
                    ) #чёрт знает какая логика!!! тут прямо в функцию, в else - через внут.сервер!!!
                    for item in gen_cp:
                        print(item)
            else:
                #работа через внутренний сервер!!!!
                #todo подумать на счёт портов
                sock = socket.socket()
                sock.connect(('localhost', 9093))
                open_signal = bytes('start_posting_wall_comments', encoding='utf8')
                #print(message)
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
                    #sock.close()
                    context['status_for_finish_of_wall_post'] = do_wall_post_form.status_for_finish_of_wall_post
                elif data =='unknown_parameter':
                    sock.close()
    #конечная ветка
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
            #ветка для отправки в личку
            print(do_privat_message_form)
            vk_group_id_for_privat_ms = do_privat_message_form.cleaned_data.get('vk_group_id_2')
            api, conn, cur = get_important_params()
            print(vk_group_id_for_privat_ms)

            res = final_sending_privat_message(api, conn, cur, vk_group_id_for_privat_ms)
            context['status_for_start_of_privat_distr']= do_privat_message_form.status_for_start_of_sending_privat_messages

        elif do_privat_multisender_sending_mess_form.is_valid():
            #ветка для отправки в личку от имеющегося множества сендеров последовательно
            print('Отправка в режиме Мультисендер')
            vk_group_id_for_privat_ms = do_privat_multisender_sending_mess_form.cleaned_data.get('vk_group_id_multisender')
            print(vk_group_id_for_privat_ms)
            for bot in BotsSenders.objects.all():
                if not bot.is_blocked:
                    access_token = bot.vk_token
                    #todo возможно следует хранить api-объект пользователя??
                    api, conn, cur  = get_important_params(access_token)
                    print('получили объект api, вызываем функцию')
                    res = final_sending_privat_message(api, conn, cur, vk_group_id_for_privat_ms, count_of_end_work=2)

    do_privat_message_form = DoPrivatMessageForm()
    do_privat_multisender_sending_mess_form = DoPrivatMultisenderSendingMessForm()
    context['do_privat_message_form'] = do_privat_message_form
    context['do_privat_multisender_sending_mess_form'] =  do_privat_multisender_sending_mess_form
    return render(request, 'VKSpam_djg/distr_to_privat.html', context)



def captcha_input_form(request):
    context = {}
    if request.method == 'POST':
        enter_captcha_form = EnterCaptchaForm(request.POST)
        if  enter_captcha_form.is_valid():

            inputed_captcha = enter_captcha_form.cleaned_data.get('inputed_captcha')
            kind_of_distribution = enter_captcha_form.cleaned_data.get('kind_of_distribution')
            print('ввели капчу', inputed_captcha)
            if kind_of_distribution == False:
                sock = socket.socket()
                sock.connect(('localhost', 9092))
            elif kind_of_distribution == True:
                sock = socket.socket()
                sock.connect(('localhost', 9093))
            else:
                #по умолчанию
                sock = socket.socket()

            print("посылаем send из ветки enter_captcha")
            sock.send(b'catch_exception')
            response_data = sock.recv(1024)
            if response_data == b'handling_exception':
                print("ЗДЕЕЕЕЕСЬ ОТСЫЛАЕТСЯ ОТСЫЛАТЬСЯ КАПЧА!!")
                inputed_captcha_encode_to_send = bytes(inputed_captcha, encoding='utf8')
                sock.send(inputed_captcha_encode_to_send)
                #добавляем в контекст переменную
                context['captcha_inf']=enter_captcha_form.captcha_inf.format(inputed_captcha)
                response_data = sock.recv(1024)
                response_data = response_data.decode('utf8')
                print(response_data)
                if response_data == 'end':
                     context['status_for_finish_of_posting_ava_comment'] = DoCommentPhotoForm.status_for_finish_of_posting_ava_comment
                if response_data == 'end_wall_posting':
                     context['status_for_finish_of_wall_post'] = DoWallPostForm.status_for_finish_of_wall_post

    enter_captcha_form = EnterCaptchaForm()
    context['enter_captcha_form'] = enter_captcha_form
    #return redirect(distr_to_avas)
    return render(request, 'VKSpam_djg/distr_to_avas.html', context)



def bots_senders_params(request):

    if request.method == 'POST':
        autorisation_form = Autorisation_Form(request.POST)
        result = request.POST.get('autorisation')
        print(result)
        bot = BotsSenders.objects.get(id = result)
        print('авторизуемся под пользователемэ', bot)
        autentification_in_vk_via_web_dr(bot.vk_login, bot.vk_password, activity_time=300)

    autorisation_form = Autorisation_Form()
    bots_senders = BotsSenders.objects.all()
    context = {'bots_senders': bots_senders,
               'autorisation_form': autorisation_form
    }
    return  render(request, 'VKSpam_djg/sender_bots.html', context)



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
    context = {}
    if request.method == 'POST':
        get_set_of_tokens_form = GetSetOfTokensForm(request.POST)
        if get_set_of_tokens_form.is_valid():
            bots = BotsSenders.objects.all()
            for bot in bots:
                if not bot.is_blocked:
                    redirected_url = get_token_by_inner_driver(bot.vk_login, bot.vk_password)
                    token, vk_user_id =  parse_and_save_auth_params(redirected_url)
                    bot.vk_token = token
                    bot.save()
            context['finish_of_getting_tokens'] = get_set_of_tokens_form.finish_of_getting_tokens

    get_set_of_tokens_form = GetSetOfTokensForm()
    context['get_set_of_tokens_form'] = get_set_of_tokens_form
    return  render(request, 'VKSpam_djg/sender_bots.html', context)

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