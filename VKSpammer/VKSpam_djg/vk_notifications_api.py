import logging
from datetime import datetime
from app_info import vk_api_version
from app_info import get_important_params


class VkNotifications:

    logger = logging.getLogger('VkNotifications')
    logger.setLevel(logging.INFO)
    sleep_time = 3
    chromeDriverPath = '/home/grishaev/PycharmProjects/VKSpammer/WebDriver/chromedriver'

    def __init__(self, bot_sender):
        self.bot_sender = bot_sender
        self.api, self.conn, self.cur = get_important_params(self.bot_sender.vk_token)

    def get_all_mentions(self) -> dict:
        all_mentions = self.api.notifications.get(filters='mentions', v=vk_api_version)
        self.logger.info(
            "{} - для пользователя {} получены упоминания: {}",
            datetime.now(),
            self.bot_sender,
            all_mentions
        )
        print("{} - для пользователя {} получены упоминания: {}".format(
            datetime.now(),
            self.bot_sender,
            all_mentions)
        )

        return all_mentions

    def mark_as_viewed(self) -> int:
        return self.api.notifications.mark_as_viewed()

# if __name__ == "__main__":
#     vkNotification = VkNotifications()
