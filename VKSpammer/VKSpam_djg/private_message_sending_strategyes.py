import logging
import random
from multiprocessing import Process
from multiprocessing import RLock
from datetime import datetime
from abc import abstractmethod
from abc import ABC
from .selenium_sender import SeleniumSender
from selenium.common.exceptions import ElementNotVisibleException as elementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from .VKCommunicatorExceptions import TooFarLastAutorisationException
from .models import VkGroupUserUnion2, BotsSenders, GorkiyGroupUser


class PrivateMessagingStrategy(ABC):

    logger = None
    multitext_list = None
    users_list = None

    @abstractmethod
    def send_private_message(self) -> None:
        pass

    def _send_private_message(self, bot):
        try:
            # todo возможно следует хранить api-объект пользователя??
            self.logger.info('открываем браузер для бота: {}'.format(bot))
            print('открываем браузер для бота: {}'.format(bot))
            selenium_sender = SeleniumSender(bot)
            sent = False
            while not sent:
                try:
                    message_index = random.randint(0, len(self.multitext_list) - 1)
                    with RLock():
                        recipient = self.users_list.pop()
                    self.logger.info(
                        "message_index:{}; recipient_first_name: {}; recipient_last_name: {}".format(
                            message_index,
                            recipient.first_name,
                            recipient.last_name
                        )
                    )

                    message_to_send = self.multitext_list[message_index].format(recipient.first_name)
                    self.logger.info("{} - сообщение для отправки: {}".format(datetime.now(), message_to_send))

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
                    self.logger.info("{} - to far last autorisation from recipient: {}".format(
                        datetime.now(),
                        recipient
                    ))
                    recipient.can_write_private_message = False
                    recipient.save()
                except elementNotVisibleException:
                    recipient.can_write_private_message = False
                    recipient.save()
                    self.logger.info("can't write message to recipient: {}".format(recipient))

        except NoSuchElementException as n_ex:
            self.logger.info(
                "{} - No such element exceptions caught: {}, {}".format(datetime.now(), recipient, n_ex))

        except WebDriverException as w_ex:
            self.logger.info("{} - WebDriverException caught: {}, {}".format(datetime.now(), recipient, w_ex))


class MessagingToPrivate:

    def __init__(self, is_multiprocess, multitexts: list, users_for_send: list, start_sender: int = 1):
        if is_multiprocess:
            self.strategy = \
                MultiprocessingThroughFakeBrowsersPrivateMessagingStrategy(start_sender, multitexts, users_for_send)
        else:
            self.strategy = \
                OneProcessThroughFakeBrowserPrivateMessagingStrategy(start_sender, multitexts, users_for_send)

    @property
    def strategy(self) -> PrivateMessagingStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: PrivateMessagingStrategy) -> None:
        self._strategy = strategy


class MultiprocessingThroughFakeBrowsersPrivateMessagingStrategy(PrivateMessagingStrategy):

    logger = logging.getLogger('MultiprocessingThroughFakeBrowsersPrivateMessagingStrategy')
    logger.setLevel(logging.INFO)

    def __init__(self, start_sender_id: int, multitexts: list, users_for_send: list):
        self.start_sender_id = start_sender_id
        self.multitext_list = multitexts
        self.users_set = users_for_send

    def send_private_message(self) -> None:
        bots_senders = BotsSenders.objects.order_by("id").filter(id__gt=self.start_sender_id)

        processes = []
        for bot in bots_senders:  # BotsSenders.objects.order_by("id"):
            if len(processes) < 5:
                from django.db import connection
                connection.close()

                process = Process(target=self._send_private_message, args=(bot, self.users_set.pop()))
                processes.append(process)
                process.start()

        for process in processes:
            process.join()

        print(processes)


class OneProcessThroughFakeBrowserPrivateMessagingStrategy(PrivateMessagingStrategy):

    logger = logging.getLogger('OneProcessThroughFakeBrowserPrivateMessagingStrategy')
    logger.setLevel(logging.INFO)

    def __init__(self, start_sender_id, multitexts: list, users: list):
        self.multitext_list = multitexts
        self.users_list = users
        self.start_sender_id = start_sender_id

    def send_private_message(self) -> None:
        bots_senders = BotsSenders.objects.order_by("id").filter(id__gt=self.start_sender_id)

        for bot in bots_senders:
            # todo грязный хак
            if not bot.is_blocked and bot.id >= self.start_sender_id:  # 0 < bot.id < 52:  # > bot.id >= 38:
                self._send_private_message(bot)

