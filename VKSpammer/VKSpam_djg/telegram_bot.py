import requests


class TelegramBot:

    main_url = 'https://api.telegram.org/{}/{}'
    bot_name = 't.me/botVkCommunicatorNotificationBot'
    token = 'bot1483003607:AAFM2WpmPNGIh8JOlZntwoycQxNrzKoIAQ8'

    # def __init__(self):
    #     pass

    def get_updates(self):
        result = requests.get(self.main_url.format(self.token, 'getUpdates'))
        print(result.text)
        print(result.json()['result'][1]['message']['text'])

    def get_user_id_for_mark_notification_as_viewed(self):
        result = requests.get(self.main_url.format(self.token, 'getUpdates'))
        print(result.text)
        print(result.json()['result'][0]['message']['text'])
        command = result.json()['result'][0]['message']['text']
        if not command.find("done") == -1:
            user_to_mark_viewed_notification = command.split("@")[1]
            print(user_to_mark_viewed_notification)
            return user_to_mark_viewed_notification
        else:
            print("что-то пошло не так")

    def send_message(self, message):
        query_params = {'chat_id':  393369302, 'text': message}
        result = requests.get(self.main_url.format(self.token, 'sendMessage'), query_params)
        print(result.request.url)


if __name__ == '__main__':

    telegram_bot = TelegramBot()
    telegram_bot.get_updates()
    telegram_bot.send_message("охренеть, как круто")
    telegram_bot.get_user_id_for_mark_notification_as_viewed()

    """
        / newbot - create
        a
        new
        bot
        / mybots - edit
        your
        bots[beta]

        Edit
        Bots
        / setname - change
        a
        bot
        's name
        / setdescription - change
        bot
        description
        / setabouttext - change
        bot
        about
        info
        / setuserpic - change
        bot
        profile
        photo
        / setcommands - change
        the
        list
        of
        commands
        / deletebot - delete
        a
        bot

        Bot
        Settings
        / token - generate
        authorization
        token
        / revoke - revoke
        bot
        access
        token
        / setinline - toggle
        inline
        mode(https: // core.telegram.org / bots / inline)
        / setinlinegeo - toggle
        inline
        location
        requests(https: // core.telegram.org / bots / inline  # location-based-results)
                           / setinlinefeedback - change
        inline
        feedback(https: // core.telegram.org / bots / inline  # collecting-feedback) settings
                           / setjoingroups - can
        your
        bot
        be
        added
        to
        groups?
        / setprivacy - toggle
        privacy
        mode(https: // core.telegram.org / bots
        # privacy-mode) in groups

        Games
        / mygames - edit
        your
        games(https: // core.telegram.org / bots / games) [beta]
                                                          / newgame - create
        a
        new
        game(https: // core.telegram.org / bots / games)
        / listgames - get
        a
        list
        of
        your
        games
        / editgame - edit
        a
        game
        / deletegame - delete
        an
        existing
        game
        """
