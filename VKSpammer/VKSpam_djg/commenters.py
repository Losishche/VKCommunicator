import logging
from django.utils import timezone
from django.db.models import QuerySet
from abc import abstractmethod
from abc import ABC
from .models import AvaMessages
from .models import BotsSenders
from app_info import do_comment_photo
from app_info import multiproc_do_comment_photo
from app_info import get_vk_api_object
from datetime import datetime
from app_info import get_important_params
from app_info import day_ava_message_limit


class CommenterStrategy(ABC):

    @abstractmethod
    def post_photo_comment(self) -> None:
        pass


class Commenter:

    def __init__(
            self,
            bot_sender: BotsSenders,
            vk_aim_group_id,
            is_auto_captcha: bool,
            is_sex_considered: bool,
            is_multitext: bool,
            is_multisender=False
            ) -> None:
        if is_multisender and is_auto_captcha and not is_sex_considered and is_multitext:
            self.strategy = \
                AutoCaptchaSexDoesntConsideredOneThreadMultiSenderBotsSendStrategy(None, vk_aim_group_id)
        elif is_auto_captcha and is_sex_considered and is_multitext:
            self.strategy = AutoCaptchaSexConsideredMultiTextSendStrategy(bot_sender, vk_aim_group_id)
        elif is_auto_captcha and is_sex_considered and not is_multitext:
            self.strategy = AutoCaptchaSexConsideredOneTextSendStrategy(bot_sender, vk_aim_group_id)
        elif is_auto_captcha and not is_sex_considered and is_multitext:
            self.strategy = AutoCaptchaSexDoesntConsideredMultiTextSendStrategy(bot_sender, vk_aim_group_id)
        elif is_auto_captcha and not is_sex_considered and not is_multitext:
            self.strategy = AutoCaptchaSexDoesntConsideredOneTextSendStrategy(bot_sender, vk_aim_group_id)

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

    def post_photo_comment(self) -> None:

        gen_cp = do_comment_photo(
            self.api,
            None,
            None,
            self.vk_aim_group_id,
            consider_user_sex=True,
            is_run_from_interface=True,
            auto_captcha=True,
            is_multitext=self.texts,
            bot_sender=self.bot_sender
        )
        print(datetime.now(), "КАКОЙ_ТО ОЧЕНЬ СТРАННЫЙ БАГ c генераторами и что там я уж не помню", gen_cp)
        for item in gen_cp:
            print('{} - iteration_of_gen: {}'.format(datetime.now(), item))
            self.logger.info('{} - iteration_of_gen: {}'.format(datetime.now(), item))


class AutoCaptchaSexDoesntConsideredMultiTextSendStrategy(CommenterStrategy):

    logger = logging.getLogger('AutoCaptchaSexDoesntConsideredMultiTextSendStrategy')
    logger.setLevel(logging.INFO)

    def __init__(self, bot_sender, vk_aim_group_id) -> None:
        self.texts = AvaMessages.objects
        self.bot_sender = bot_sender
        self.api = get_vk_api_object(bot_sender.vk_token)
        self.vk_aim_group_id = vk_aim_group_id

    def post_photo_comment(self) -> None:

        gen_cp = do_comment_photo(
            self.api,
            None,
            None,
            self.vk_aim_group_id,
            consider_user_sex=False,
            is_run_from_interface=True,
            auto_captcha=True,
            is_multitext=self.texts,
            bot_sender=self.bot_sender
        )
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

        gen_cp = do_comment_photo(
            self.api,
            None,
            None,
            self.vk_aim_group_id,
            consider_user_sex=False,
            is_run_from_interface=True,
            auto_captcha=True,
            bot_sender=self.bot_sender
        )
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

        gen_cp = do_comment_photo(
            self.api,
            None,
            None,
            self.vk_aim_group_id,
            consider_user_sex=True,
            is_run_from_interface=True,
            auto_captcha=True,
            bot_sender=self.bot_sender
        )
        print(datetime.now(), "КАКОЙ_ТО ОЧЕНЬ СТРАННЫЙ БАГ c генераторами и что там я уж не помню", gen_cp)
        for item in gen_cp:
            print('{} - iteration_of_gen: {}'.format(datetime.now(), item))
            self.logger.info('{} - iteration_of_gen: {}'.format(datetime.now(), item))


class AutoCaptchaSexDoesntConsideredOneThreadMultiSenderBotsSendStrategy(CommenterStrategy):

    logger = logging.getLogger("AutoCaptchaSexConsideredOneThreadMultiSenderBotsSendStrategy")
    logger.setLevel(logging.INFO)

    def __init__(self, bots_senders_set: None, vk_aim_group_id) -> None:
        self.set_of_senders = BotsSenders.objects.filter(is_blocked=False).order_by("id")[20:]
        self.vk_aim_group_id = vk_aim_group_id
        self.users_api = []
        self.logger.info("{} - выбрана стратегия отправки мультисендер без мультипроцессинга".format(datetime.now()))

    def post_photo_comment(self) -> None:
        for bot in self.set_of_senders:
            print('{} - start distribution with bot: {}'.format(datetime.now(), str(bot)))
            self.logger.info('{} - start distribution with bot: {}'.format(datetime.now(), str(bot)))
            # date_offset = NaiveTZInfo(+3)
            if bot.date_of_starting_day_counting is None:
                bot.date_of_starting_day_counting = timezone.now()
                bot.save()

            if (timezone.now() - bot.date_of_starting_day_counting).days >= 1:
                bot.date_of_starting_day_counting = timezone.now()
                bot.day_sent_message_count = 0
                bot.save()
                # todo убрать избыточность кода
                # users_api.append(get_important_params(bot.vk_token))
                api, conn, cur = get_important_params(bot.vk_token)
                texts = AvaMessages.objects

                gen_cp = do_comment_photo(
                    api,
                    conn,
                    cur,
                    self.vk_aim_group_id,
                    consider_user_sex=False,
                    is_run_from_interface=True,
                    auto_captcha=True,
                    is_multitext=texts,
                    bot_sender=bot
                )
                # чёрт знает какая логика!!! тут прямо в функцию, в else - через внут.сервер!!!
                for item in gen_cp:
                    self.logger.info("{} - из функции-генератора получено значение {}".format(datetime.now(), item))
            if (timezone.now() - bot.date_of_starting_day_counting).days < 1 \
                    and bot.day_sent_message_count < day_ava_message_limit:
                api, conn, cur = get_important_params(bot.vk_token)
                texts = AvaMessages.objects
                # users_api.append(get_important_params(bot.vk_token)[0])
                gen_cp = do_comment_photo(
                    api,
                    conn,
                    cur,
                    self.vk_aim_group_id,
                    consider_user_sex=False,
                    is_run_from_interface=True,
                    auto_captcha=True,
                    is_multitext=texts,
                    bot_sender=bot
                )

                for item in gen_cp:
                    print(item)
                    self.logger.info('user: {}'.format(item))
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




