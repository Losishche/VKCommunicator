
class MessageToFriendSender:

    def __init__(self, user_name, user_text=None):
        if user_text is None:
            self.user_text = "Привет, {}".format(user_name)
        else:
            self.user_text = user_text.format(user_text)

    def make_message_to_private(self, user_name, user_text=None, is_multitext=False):
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
            logger_for_communicator.info('Текст для отправки: {}'.format(user_text))
        elif user_text.find('{}') != -1:
            user_text = user_text.format(user_name)

        return user_text