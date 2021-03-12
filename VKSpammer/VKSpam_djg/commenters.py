import logging
import socket
import time

import vk
from django.utils import timezone
from abc import abstractmethod
from abc import ABC

from work_with_DB import update_vk_photo_comment_state_group_user_union
from .models import AvaMessages
from .models import BotsSenders
from app_info import multiproc_do_comment_photo, connection_to_postgres, select_group_users_union, logger, \
    _do_like_inside_commenting_photo_process, DoCommenter, PhotoCommentExceptionsExpert
from app_info import get_vk_api_object
from datetime import datetime
from app_info import get_important_params
from app_info import day_ava_message_limit


class CommenterStrategy(ABC):

    @abstractmethod
    def post_photo_comment(self) -> None:
        pass

    def do_comment_photo(self, api, pg_con, pg_cur, group_id, consider_user_sex=False, is_run_from_interface=False,
                         delay_between_posts=3, auto_captcha=False, is_multitext=False, message_limit=90,
                         bot_sender=None, users_list=None):
        """
        комментирование аватарок
        :param self:
        :param api:
        :param pg_con:
        :param pg_cur:
        :param group_id:
        :param consider_user_sex:
        :param is_run_from_interface:
        :param delay_between_posts:
        :param auto_captcha:
        :param is_multitext:
        :param message_limit:
        :param bot_sender:
        :param users_list:
        :return:
        """
        if pg_con is None and pg_cur is None:
            pg_con, pg_cur = connection_to_postgres()

        # если параметр is_multitext передается, то тексты передаются в нём!!
        message_text = is_multitext if is_multitext else '{}, С новым годом!)))'
        # list_of_vk_errors = select_vk_errors(pg_con, pg_cur)

        # костыль для отправки посредством мультипроцессинга, но что поделать!!
        tupl_members_inner = select_group_users_union(pg_con, pg_cur, group_id) if users_list is None else users_list
        count = 0
        for user in tupl_members_inner:

            if user[9] is True and user[5] is not True and user[6] is not True:
                print("{} - работаем с пользователем ВК {}".format(datetime.now(), user))
                logger.info("{} - работаем с пользователем ВК {}".format(datetime.now(), user))
                # ставим лайк
                _do_like_inside_commenting_photo_process(api, user, is_run_from_interface, delay_between_posts)
                do_commenter = DoCommenter(user, message_text, is_multitext)
                # делаем пост под фото внутри try и перехватываем возможные исключения
                try:
                    do_commenter.create_photo_comment_considering_sex(api, consider_user_sex)
                    update_vk_photo_comment_state_group_user_union(pg_con, pg_cur, user[1])
                    logger.info("{} - ava comment posted successful to {}".format(datetime.now(), user))
                    count += 1
                    if bot_sender:
                        bot_sender.day_sent_message_count += 1
                        bot_sender.save()
                except vk.exceptions.VkAPIError as err:
                    logging.info('{} - получена ошибка при попытке коммента: ', datetime.now(), err)
                    print(datetime.now(), ' - получена ошибка при попытке коммента:', err)

                    exception_expert = PhotoCommentExceptionsExpert(pg_con, pg_cur, err, user, auto_captcha)
                    handle_exception_result = exception_expert.handle_concrete_error()
                    if handle_exception_result == 'stop':
                        break
                    if handle_exception_result == 'continue':
                        continue
                        # надо решить, где это должно быть
                        # update_vk_photo_comment_state_group_user_union(
                        #     postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
                    else:
                        # try-ветка на случай повторного исключения необходимости капчи
                        try:
                            do_commenter.create_photo_after_captcha(
                                api, err.error_data['captcha_sid'], handle_exception_result
                            )
                            print(datetime.now(), ' - SUCCESSfully сделан пост после разгадки капчи: ', user)
                            logger.info("{} - успешно сделан пост после разгадки капчи пользователю {}".format(
                                datetime.now(),
                                user)
                            )
                            update_vk_photo_comment_state_group_user_union(pg_con, pg_cur, user[1])  # пилят
                            count += 1
                            if bot_sender:
                                bot_sender.day_sent_message_count += 1
                                bot_sender.save()
                            #     if bot_sender.day_sent_message_count == limit_count_of_message:
                            #         break
                        except vk.exceptions.VkAPIError as err:
                            if err.is_captcha_needed() is True and err.message == 'Captcha needed':
                                print(datetime.now(), " - неверно разгадали капчу: ", user[0])
                                # todo продумать, что делать, если неверно разгадали капчу
                                # exception_expert =
                                # PhotoCommentExceptionsExpert(postgres_con, postgres_cur, erro, user)
                                # handle_exception_result = exception_expert.handle_concrete_error()
                                # print(datetime.now(),
                                #       " - неверно ввели капчу второй раз, третий раз капчу не запрашиваем:",
                                #       user
                                #       )
                            # todo продумать, как правильнее обработать другие исключения, после отправки с разг. капчей
                            else:
                                print(err)
                except Exception as err:
                    logger.info('{} - возникло критическое исключение, {}, {}'.format(datetime.now(), bot_sender, err))
                    print(err)
                time.sleep(delay_between_posts)
            else:
                logger.info('{} - не осталось пользователей для комментов в группе: {}'.format(datetime.now(), group_id))
                print('{} - не осталось пользователей для комментов в группе, {}'.format(datetime.now(), group_id))
                print('{} - черт знает.. {}'.format(datetime.now(), group_id))
                # break

    # todo нахрена этот метод здесь?
    def _check_bot_sender_limit(self, bot_sender, message_limit, count) -> bool:
        if bot_sender:
            if bot_sender.day_sent_message_count > message_limit:
                print(datetime.now(), bot_sender, " - message limit for sender reached, distribution is finished")
                logger.info("{} - message limit for sender is reached, distribution is finished: {}"
                            .format(datetime.now(), bot_sender))
                return False
        # два счетчика тут для работы не только из админки, но и из консоли??
        if count > message_limit:
            print(datetime.now(), bot_sender, " - default message limit for sender reached, distribution finished")
            logger.info("{} - default message limit for sender is reached, distribution is finished: {}"
                        .format(datetime.now(), bot_sender))
            return False
        return True

    def _check_bot_sender_counting_limit(self, bot) -> bool:
        if bot.date_of_starting_day_counting is None:
            bot.date_of_starting_day_counting = timezone.now()
            bot.save()
        if (timezone.now() - bot.date_of_starting_day_counting).days >= 1:
            bot.date_of_starting_day_counting = timezone.now()
            bot.day_sent_message_count = 0
            bot.save()
            return True
        if (timezone.now() - bot.date_of_starting_day_counting).days < 1 \
                and bot.day_sent_message_count < day_ava_message_limit:
            return True
        return False


class Commenter:

    def __init__(
            self,
            bot_sender: BotsSenders,
            vk_aim_group_id,
            is_auto_captcha: bool,
            is_sex_considered: bool,
            is_multitext: bool,
            is_multisender=False,
            message="") -> None:
        if is_auto_captcha and is_multisender and not is_sex_considered and is_multitext:
            self.strategy = \
                AutoCaptchaSexDoesntConsideredOneThreadMultiSenderBotsSendStrategy(bot_sender, vk_aim_group_id)
        elif is_auto_captcha and is_sex_considered and is_multitext:
            self.strategy = AutoCaptchaSexConsideredMultiTextSendStrategy(bot_sender, vk_aim_group_id)
        elif is_auto_captcha and is_sex_considered and not is_multitext:
            self.strategy = AutoCaptchaSexConsideredOneTextSendStrategy(bot_sender, vk_aim_group_id)
        elif is_auto_captcha and not is_sex_considered and is_multitext:
            self.strategy = AutoCaptchaSexDoesntConsideredMultiTextSendStrategy(bot_sender, vk_aim_group_id)
        elif is_auto_captcha and not is_sex_considered and not is_multitext:
            self.strategy = AutoCaptchaSexDoesntConsideredOneTextSendStrategy(bot_sender, vk_aim_group_id)
        elif not is_auto_captcha:
            self.strategy = NoAutoCaptchaMultiText(bot_sender, vk_aim_group_id, message)
        elif not is_auto_captcha and not is_multitext:
            self.strategy = NoAutoCaptchaSingleText(bot_sender, vk_aim_group_id, message)

    @property
    def strategy(self) -> CommenterStrategy:
        """
        The Context maintains a reference to one of the Strategy objects. The
        Context does not know the concrete class of a strategy. It should work
        with all strategies via the Strategy interface.
        """

        return self._strategy

    @strategy.setter
    def strategy(self, strategy: CommenterStrategy) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """

        self._strategy = strategy

    # def do_some_business_logic(self) -> None:
    #     """
    #     The Context delegates some work to the Strategy object instead of
    #     implementing multiple versions of the algorithm on its own.
    #     """
    #
    #     # ...
    #
    #     print("Context: Sorting data using the strategy (not sure how it'll do it)")
    #     result = self._strategy.post_photo_comment()
    #     print(",".join(result))


class AutoCaptchaSexConsideredMultiTextSendStrategy(CommenterStrategy):

    logger = logging.getLogger('AutoCaptchaSexConsideredMultiTextSendStrategy')
    logger.setLevel(logging.INFO)

    def __init__(self, bot_sender, vk_aim_group_id) -> None:
        self.texts = AvaMessages.objects
        self.bot_sender = bot_sender
        self.api = get_vk_api_object(bot_sender.vk_token)
        self.vk_aim_group_id = vk_aim_group_id
        self.logger.info(
            "{} - выбрана стратегия отправки комментариев к фото - ".format(datetime.now(), self.__name__())
        )

    def post_photo_comment(self) -> None:
        gen_cp = self.do_comment_photo(self.api, None, None, self.vk_aim_group_id, consider_user_sex=True,
                                  is_run_from_interface=True, auto_captcha=True, is_multitext=self.texts,
                                  bot_sender=self.bot_sender)
        print(datetime.now(), "КАКОЙ_ТО ОЧЕНЬ СТРАННЫЙ БАГ c генераторами и что там я уж не помню", gen_cp)
        for item in gen_cp:
            print('{} - iteration_of_gen: {}'.format(datetime.now(), item))
            self.logger.info('{} - iteration_of_gen: {}'.format(datetime.now(), item))


class NoAutoCaptchaSingleText(CommenterStrategy):
    logger = logging.getLogger('NoAutoCaptchaSendStrategy')
    logger.setLevel(logging.INFO)

    def __init__(self, bot_sender, vk_group_id, single_text) -> None:
        self.texts = AvaMessages.objects
        self.bot_sender = bot_sender
        self.api = get_vk_api_object(bot_sender.vk_token)
        self.vk_group_id = vk_group_id
        self.message = single_text
        print("{} - выбрана стратегия отправки комментариев к фото - {}".format(datetime.now(), self.__str__()))
        self.logger.info(
            "{} - выбрана стратегия отправки комментариев к фото - {}".format(datetime.now(), self.__str__())
        )

    def post_photo_comment(self) -> None:
        self.do_comment_photo(self.api, None, None, self.vk_group_id, consider_user_sex=True,
                              is_run_from_interface=True, auto_captcha=False, is_multitext=False,
                              bot_sender=self.bot_sender)

    # def post_photo_comment(self) -> None:
    #     # todo костыльные внутренние серверы блин
    #     # работа через внутренний сервер!!!! эксперименты, мать их...не получается из за них использовать стратегию..
    #     sock = socket.socket()
    #     sock.connect(('localhost', 9092))
    #     open_signal = bytes('start_commenting_photo', encoding='utf8')
    #     # print(message)
    #     sock.send(open_signal)
    #     data = sock.recv(1024)
    #     if data == b'start_commenting_photo_resp':
    #         parameters = self.vk_group_id + ', ' + self.message
    #         parameters = bytes(parameters, encoding='utf8')
    #         sock.send(parameters)
    #         # context['status_for_start_of_posting_ava_comment'] = \
    #         #     do_comment_photo_form.status_for_start_of_posting_ava_comment
    #         data = sock.recv(1024)
    #         # std_out_messages = open('/home/grishaev/PycharmProjects/VKSpammer/test_stdout')
    #         std_out_messages = open('../test_stdout')
    #         # context['std_out_messages'] = std_out_messages.readline()
    #         # if data == b'cought_exeption':
    #         # context['status_for_cought_exeption'] = '!!!!'  # что ЭТО такое??
    #     print("{} - значение протокола, полученное от 'внутреннего сервера': {}".format(datetime.now(), data))
    #     if data == 'end':
    #         print("ну, случилась data end и что с того?")
    #         # sock.close()
    #         # context['status_for_finish_of_posting_ava_comment'] = \
    #         #     do_comment_photo_form.status_for_finish_of_posting_ava_comment
    #     elif data == 'unknown_parameter':
    #         sock.close()


class NoAutoCaptchaMultiText(CommenterStrategy):
    logger = logging.getLogger('NoAutoCaptchaMultiTextSendStrategy')
    logger.setLevel(logging.INFO)

    def __init__(self, bot_sender, vk_group_id, messages) -> None:
        self.texts = AvaMessages.objects
        self.bot_sender = bot_sender
        self.api = get_vk_api_object(bot_sender.vk_token)
        self.vk_group_id = vk_group_id
        self.message = messages
        print(
            "{} - выбрана стратегия отправки комментариев к фото - {}".format(datetime.now(), self.__str__())
        )
        self.logger.info(
            "{} - выбрана стратегия отправки комментариев к фото - {}".format(datetime.now(), self.__str__())
        )

    def post_photo_comment(self) -> None:
        self.do_comment_photo(self.api, None, None, self.vk_group_id, consider_user_sex=True,
                              is_run_from_interface=True, auto_captcha=False, is_multitext=self.texts,
                              bot_sender=self.bot_sender)


class AutoCaptchaSexDoesntConsideredMultiTextSendStrategy(CommenterStrategy):

    logger = logging.getLogger('AutoCaptchaSexDoesntConsideredMultiTextSendStrategy')
    logger.setLevel(logging.INFO)

    def __init__(self, bot_sender, vk_aim_group_id) -> None:
        self.texts = AvaMessages.objects
        self.bot_sender = bot_sender
        self.api = get_vk_api_object(bot_sender.vk_token)
        self.vk_aim_group_id = vk_aim_group_id

    def post_photo_comment(self) -> None:

        gen_cp = self.do_comment_photo(self.api, None, None, self.vk_aim_group_id, consider_user_sex=False,
                                  is_run_from_interface=True, auto_captcha=True, is_multitext=self.texts,
                                  bot_sender=self.bot_sender)
        print(datetime.now(), "КАКОЙ_ТО ОЧЕНЬ СТРАННЫЙ БАГ c генераторами и что там я уж не помню", gen_cp)
        for item in gen_cp:
            print('{} - iteration_of_gen: {}'.format(datetime.now(), item))
            self.logger.info('{} - iteration_of_gen: {}'.format(datetime.now(), item))


class AutoCaptchaSexDoesntConsideredOneTextSendStrategy(CommenterStrategy):

    logger = logging.getLogger('AutoCaptchaSexDoesntConsideredOneTextSendStrategy')
    logger.setLevel(logging.INFO)

    def __init__(self, bot_sender, vk_aim_group_id) -> None:
        self.texts = AvaMessages.objects
        self.bot_sender = bot_sender
        self.api = get_vk_api_object(bot_sender.vk_token)
        self.vk_aim_group_id = vk_aim_group_id

    def post_photo_comment(self) -> None:

        gen_cp = self.do_comment_photo(self.api, None, None, self.vk_aim_group_id, consider_user_sex=False,
                                       is_run_from_interface=True, auto_captcha=True, bot_sender=self.bot_sender)
        print(datetime.now(), "КАКОЙ_ТО ОЧЕНЬ СТРАННЫЙ БАГ c генераторами и что там я уж не помню", gen_cp)
        for item in gen_cp:
            print('{} - iteration_of_gen: {}'.format(datetime.now(), item))
            self.logger.info('{} - iteration_of_gen: {}'.format(datetime.now(), item))


class AutoCaptchaSexConsideredOneTextSendStrategy(CommenterStrategy):

    logger = logging.getLogger('AutoCaptchaSexConsideredAlwaysOneTextSendStrategyLogger')
    logger.setLevel(logging.INFO)

    def __init__(self, bot_sender, vk_aim_group_id) -> None:
        self.bot_sender = bot_sender
        self.api = get_vk_api_object(bot_sender.vk_token)
        self.vk_aim_group_id = vk_aim_group_id

    def post_photo_comment(self) -> None:

        self.do_comment_photo(self.api, None, None, self.vk_aim_group_id, consider_user_sex=True,
                              is_run_from_interface=True, auto_captcha=True, bot_sender=self.bot_sender)


class AutoCaptchaSexDoesntConsideredOneThreadMultiSenderBotsSendStrategy(CommenterStrategy):

    logger = logging.getLogger("AutoCaptchaSexConsideredOneThreadMultiSenderBotsSendStrategy")
    logger.setLevel(logging.INFO)
    auto_captcha = True
    texts = AvaMessages.objects

    def __init__(self, bots_senders_set: BotsSenders, vk_aim_group_id) -> None:
        self.set_of_senders = bots_senders_set  # BotsSenders.objects.filter(is_blocked=False).order_by("id")[20:]
        self.vk_aim_group_id = vk_aim_group_id
        self.logger.info("{} - выбрана стратегия отправки мультисендер/мультитекст без мультипроцессинга"
                         .format(datetime.now()))

    def post_photo_comment(self) -> None:
        for bot in self.set_of_senders:
            print('{} - start distribution with bot: {}'.format(datetime.now(), str(bot)))
            self.logger.info('{} - start distribution with bot: {}'.format(datetime.now(), str(bot)))
            # date_offset = NaiveTZInfo(+3)
            if self._check_bot_sender_counting_limit(bot):
                api, conn, cur = get_important_params(bot.vk_token)

                self.do_comment_photo(api, conn, cur, self.vk_aim_group_id, consider_user_sex=False,
                                      is_run_from_interface=True, auto_captcha=self.auto_captcha,
                                      is_multitext=self.texts, bot_sender=bot)
            else:
                self.logger.info('{}: дневной лимит для пользователя "{}" исчерпан'.format(datetime.now(), bot))
                print('{}: дневной лимит для пользователя "{}" исчерпан'.format(datetime.now(), bot))


# пока не используется
class AutoCaptchaSexConsideredMultiprocessMultiSenderBotsSendStrategy(CommenterStrategy):

    logger = logging.getLogger('AutoCaptchaSexConsideredMultiprocessMultiSenderBotsSendStrategy')
    logger.setLevel(logging.INFO)

    def __init__(self, bot_senders_set: set, vk_aim_group_id) -> None:
        self.set_of_senders = bot_senders_set[20:]
        self.vk_aim_group_id = vk_aim_group_id
        self.users_api = []

    def post_photo_comment(self) -> None:

        for bot in self.set_of_senders:
            print(datetime.now(), ' - start distribution with bot', bot)
            self.logger.info('{} - start distribution with bot: {}'.format(datetime.now(), bot))
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
                self.users_api.append(list(get_important_params(bot.vk_token)) + [bot])
                # api, conn, cur = get_important_params(bot.vk_token)

            if (timezone.now() - bot.date_of_starting_day_counting).days < 1 and bot.day_sent_message_count < 90:
                api, conn, cur = get_important_params(bot.vk_token)
                # texts = AvaMessages.objects
                self.users_api.append(list(get_important_params(bot.vk_token)) + [bot])
            else:
                self.logger.info('{} - day`s limit for sender "{}" is exceeded'.format(datetime.now(), bot.surname))
                print('{} - day`s limit for sender "{}" is exceeded'.format(datetime.now(), bot.surname))

            # sleep(300)
            multiproc_do_comment_photo(
                self.users_api,
                conn,
                cur,
                self.vk_group_id,
                consider_user_sex=True,
                is_run_from_interface=True,
                auto_captcha=True,
                is_multitext=self.texts,
                # bot_sender = api_u[3]
            )

            # # ветка обработки исключений
            # if erro.code == 7:  # error_data - это uсловарь, где хранятся данные о вернувшейся ошибке api
            #     if erro.message == 'Permission to perform this action is denied: photo is deleted':
            #         print(datetime.now(), ' - ', user, ', ', 'обновляем инфо о фото в БД из-за ошибки ', erro)
            #         update_vk_photo_comment_state_group_user_union(
            #             postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
            #         # todo делать запись в БД!!!!
            #     elif erro.message == 'Permission to perform this action is denied: user is not allowed to comment':
            #         print(erro, 'обновляем инфо о фото в БД')
            #         update_vk_photo_comment_state_group_user_union(
            #             postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
            #     elif erro.message == 'Permission to perform this action is denied: photo access denied':
            #         # todo проверить и если ДА - переписать на работу по ID(первичному ключу)
            #         print(erro, 'updating photo info in database')
            #         update_vk_photo_comment_state_group_user_union(
            #             postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
            #
            #     # 7 ошибка возникает, в основном, (но не всегда!) тогда, когда достигнут лимит на что-либо
            #     # и невозможно выполнить твоё действие. В этом случае завершаем отправку или нет -
            #     # не до конца ясно. Поэтому пока закомментирован функционал обновления свойств фото в бд
            #     # ПОКА раскоментировал для тестов!
            #     elif erro.message == 'Permission to perform this action is denied: wall or photo comment not added'\
            #             and len(may_be_not_possible_for_post_ava) > 0:
            #         print(
            #             "{} - got error [{}]. Сендеру, вероятно, запретили дальше слать, зайдём под другим",
            #             datetime.now(),
            #             erro)
            #         logger.info(
            #             "{} - got error [{}]. Сендеру, вероятно, запретили дальше слать, зайдём под другим"
            #             .format(datetime.now(), erro))
            #         time.sleep(delay_between_posts)
            #         break
            #     elif erro.message == 'Permission to perform this action is denied: wall or photo comment not added':
            #         may_be_not_possible_for_post_ava.append(user)
            #         print("{} - got error [{}] may be user {} haven't allowed posting ava comment",
            #               datetime.now(),
            #               erro,
            #               user)
            #         logger.info("{} - got error [{}] may be user {} haven't allowed posting ava comment"
            #                     .format(datetime.now(), erro, user))
            #         # print("{} - got error [{}] updating photo info in database", datetime.now(), erro)
            #         # logger.info("{} - got error [{}] updating photo info in db".format(datetime.now(), erro))
            #         # update_to_vk_photo_comment_state_group_user_union(
            #         #     postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
            #         # проблема в том, что ранее такая ошибка возвращалась, если достигнут лимит отправки
            #         # постов. Нужно проверить, так ли это еще и реализовать нивелирующую данное поведение, фичу
            #         # todo  впилить проверку сюда?
            #         # return may_be_not_possible_for_post_ava
            #     else:
            #         print(datetime.now(),
            #               " нужно авторизоваться под другим пользователем. Работа скрипта будет завершена"
            #               )
            #         logger.info(
            #             "{} - got error [{}]. Нужно зайти под другим пользователем. Работа скрипта будет завершена"
            #             .format(datetime.now(), erro))
            #         time.sleep(600)
            #         time.sleep(delay_between_posts)
            #         # todo подумать над доработкой&&&
            #         break
            # elif erro.error_data['error_code'] == 15:
            #     print(datetime.now(),
            #           ' - updating photo info in database for vk_user_id: ',
            #           erro.request_params['owner_id']
            #           )
            #     update_vk_photo_comment_state_group_user_union(
            #         postgres_con, postgres_cur, user[1], can_post_ava_comment=False)
            # elif erro.error_data['error_code'] == 14:
            #     print(datetime.now(), ' - ', erro.message, '; ', erro.error_data, '; ', erro.is_captcha_needed)
            #     logger.info('{} - {}; {}; {}'
            #                 .format(datetime.now(), erro.message, erro.error_data, erro.is_captcha_needed))
            #     if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
            #         save_have_got_captcha(erro)
            #         captcha_guessed = work_with_ru_captcha()
            #         # webbrowser.open_new_tab(erro.error_data['captcha_img'])
            #         print(erro.error_data['captcha_img'])
            #         # если параметр True, то функция становится генератором для приема данных
            #         # от интерфейса с помощью send
            #         if is_run_from_interface is True:
            #             captcha_inputed = yield 'handling_exception'
            #             # print("DEBUG_2", captcha_inputed)
            #             print(datetime.now(), ": отгаданная капча - ", captcha_guessed)
            #         else:
            #             captcha_inputed = input()
            #         # вторая ветка исключений (обработка) на случай неверно введённой капчи
            #         try:
            #             create_photo_comment(
            #                 api, owner_id=user[1], photo_id=user[8], message=message,
            #                 attachments=attachments_for_photo_comment_for_woman,
            #                 captcha_sid=erro.error_data['captcha_sid'],
            #                 # captcha_key=captcha_inputed
            #                 captcha_key=captcha_guessed)
            #             print('Posted SUCCESSfully!')
            #             logger.info("{} - успешно сделан пост после разгадки капчи пользователю {}".format(
            #                 datetime.now(),
            #                 user)
            #             )
            #             update_vk_photo_comment_state_group_user_union(postgres_con, postgres_cur, user[1])  # пилят
            #             count += 1
            #             if bot_sender:
            #                 bot_sender.day_sent_message_count += 1
            #                 bot_sender.save()
            #             #     if bot_sender.day_sent_message_count == limit_count_of_message:
            #             #         break
            #             #     # todo ну капец ущербная логика. сделал так только из-за отсутствия времени
            #             # if count == limit_count_of_message:
            #             #     # здесь прерываем цикл. В случае генератора, возбуждается исключение StopIteration
            #             #     # todo странная логика. проверку count нужно вынести в начало цикла
            #             #     break
            #             time.sleep(delay_between_posts)
            #         except:
            #             if erro.is_captcha_needed() is True and erro.message == 'Captcha needed':
            #                 print("Неверно ввели каптчу второй раз??")
            #             else:
            #                 print(erro)
            # else:
            #     print("Не удалось обработать ошибку и завершить действие")