import vk
import random
from time import sleep
from datetime import datetime
from work_with_DB import *


class MessageToPrivateSender:

    vk_api_version = 5.0

    def __init__(self, api, conn, cur, friends_list, vk_sender):
        self.api = api
        self.conn = conn
        self.cur = cur
        self.friends_linner_ist = friends_list  # должен быть в другом объекте
        self.vk_sender = vk_sender

    # def get_vk_senders_friends(self):
    #     if len(self.friends_linner_ist) == 0:
    #         friends_ids_list = self.api.friends.get(version=self.vk_api_version)
    #         print(friends_ids_list)
    #         self._get_user_info(friends_ids_list)
    #         return self.friends_linner_ist

    # def _get_user_info(self, friends_ids_list):
    #     """
    #     получение информации о пользователе
    #     :return:
    #     """
    #     friends_from_vk = self.api.users.get(version=self.vk_api_version, user_ids=friends_ids_list)
    #     print(self.friends_list)
    #     for friend in friends_from_vk:
    #         bot_friend = BotsFriends()
    #         bot_friend.vk_id = friend['uid']
    #         bot_friend.first_name = friend['first_name']
    #         bot_friend.last_name = friend['last_name']
    #         bot_friend.friend_bot = self.vk_sender
    #         print("{}: получен друг: {}".format(datetime.now(), bot_friend))
    #         bot_friend.save()
    #     self.friends_list = BotsFriends.objects.get()
        # return self.friends_list

    def send_invite_messages(self,
                             message_list=False,
                             pause_between_sending=60
                             ):
        """
        фактическая отсылка сообщений (вспомогательная функция)
        :param api:
        :param user_id:
        :param message_list:
        :param pause_between_sending:
        :return:
        """
        """
        :param api:
        :param user_id:
        :param message:
        :param kwargs:
        :return:
        """
        if not message_list:
            message_list = ["Приветствую, {}! Наш друг Алексей (Гитарист Горького) замутил новый проект."
                            "Вступай, вот, в группу))) https://vk.com/stars_zvezdi"]
        else:
            print("передан список пригласительных личных сообщений")
        for user in self.friends_linner_ist:
            data_dict = {
                'version': self.vk_api_version,
                'user_id': user.vk_user_id,
                'message': message_list[int(random.uniform(0, len(message_list)))].format(user.first_name),
            }
            if not user.have_sent_invite_private_messages:
                print("{}: ранее пользователю {}, {}, не отсылалось сообщение, подготовка к отправке".format(
                    datetime.now(),
                    user.vk_user_id,
                    user.last_name
                ))
                try:
                    self.api.messages.send(**data_dict)
                    print("{}: sent success to friend: {}, {}".format(datetime.now(), user.vk_user_id, user.last_name))
                    user.have_sent_invite_private_messages = True
                    if user.count_sent_private_messages:
                        user.count_sent_private_messages += 1
                    else:
                        user.count_sent_private_messages = 1
                    user.save()
                    sleep(pause_between_sending)
                except vk.exceptions.VkAPIError as error:
                    if error.code == 7:
                        print("не удалось отправить сообщение пользователю: {}".format(user.vk_user_id))

    def send_invite_messages_to_loyal_user_group(self,
                             message_list=False,
                             pause_between_sending=60
                             ):
        """
        фактическая отсылка сообщений (вспомогательная функция)
        :param api:
        :param user_id:
        :param message_list:
        :param pause_between_sending:
        :return:
        """
        """
        :param api:
        :param user_id:
        :param message:
        :param kwargs:
        :return:
        """
        if not message_list:
            message_list = ["Приветствую, {}! Наш друг Алексей (Гитарист Горького) замутил новый проект."
                            "Вступай, вот, в группу))) https://vk.com/stars_zvezdi"]
        else:
            print("передан список пригласительных личных сообщений")
        for user in self.friends_linner_ist:
            data_dict = {
                'version': self.vk_api_version,
                'user_id': user.vk_id,
                'message': message_list[int(random.uniform(0, len(message_list)))].format(user.first_name),
            }
            if not user.have_sent_invite_private_message or user.have_sent_invite_private_message is None:
                print("{}: ранее пользователю {}, {}, не отсылалось сообщение, подготовка к отправке".format(
                    datetime.now(),
                    user.vk_id,
                    user.last_name
                ))
                try:
                    self.api.messages.send(**data_dict)
                    print("{}: sent success to friend: {}, {}".format(datetime.now(), user.vk_id, user.last_name))
                    user.have_sent_invite_private_message = True
                    if user.count_sent_privat_messages:
                        user.count_sent_privat_messages += 1
                    else:
                        user.count_sent_privat_messages = 1
                    user.save()
                    sleep(pause_between_sending)
                except vk.exceptions.VkAPIError as error:
                    if error.code == 7:
                        print("не удалось отправить сообщение пользователю: {}".format(user.vk_id))
