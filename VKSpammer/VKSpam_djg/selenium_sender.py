import time
import logging
from selenium import webdriver
from .VKCommunicatorExceptions import TooFarLastAutorisationException
from selenium.common.exceptions import NoSuchElementException


class SeleniumSender:

    logger_for_communicator = logging.getLogger('logger_for_communicator')
    logger_for_communicator.setLevel(logging.INFO)
    sleep_time = 3
    message_page_url = "https://vk.com/write{}"
    public_page_url = "https://vk.com/public{}"
    write_message_elemet_of_form = "im_editable{}"
    login = ''
    password = ''
    chromeDriverPath = '/home/grishaev/PycharmProjects/VKSpammer/WebDriver/chromedriver'

    def __init__(self, bot):
        self.chrome_browser = webdriver.Chrome(chromeDriverPath)
        self.login = bot.vk_login
        self.password = bot.vk_password
        self.chrome_browser.get('https://vk.com/login')
        elem_for_email = self.chrome_browser.find_element_by_id("email")
        elem_for_pass = self.chrome_browser.find_element_by_id("pass")
        print(elem_for_pass, elem_for_email)
        elem_for_email.send_keys(self.login)
        elem_for_pass.send_keys(self.password)
        elem_for_email.submit()
        time.sleep(3)
        # self.chrome_browser = autentification_in_vk_via_web_dr(
        #     self.login, self.password, auth_url='https://vk.com/login', activity_time=0)

    # def start_distr(self):
    #     self.chrome_browser = autentification_in_vk_via_web_dr(
    #         self.login, self.password, auth_url='https://vk.com/login', activity_time=400)

    # def find_send_message_form(self):
    #     elem_for_message = self.chrome_browser.find_element_by_id("email")

    # class ="ms_item_more_label" > < span class ="blind_label" > Ещё < / span > < / span >

    def open_group_page_and_like_wall_post(self, group_page, wall_post_id):
        print(group_page, wall_post_id)
        self.chrome_browser.get(self.public_page_url.format(group_page))
        element_id = 'post-{}_{}'.format(group_page, wall_post_id)
        post_element = self.chrome_browser.find_element_by_id(element_id)
        like_element = post_element.find_element_by_class_name('like_btn like _like animate active')
        self.chrome_browser.switch_to(like_element)
        print(like_element)
        like_element.click()

        time.sleep(5)
        self.chrome_browser.close()
    #     < a
    #
    #     class ="like_btn like _like animate active" onclick="Likes.toggle(this, event, 'wall-49887978_1846', 'd7e5a7752104c8673d');" onmouseover="Likes.showLikes(this, 'wall-49887978_1846', {})" data-count="87" href="#" title="Нравится" >
    #
    #     < div
    #
    #     class ="like_button_icon" > < / div >
    #
    #     < div
    #
    #     class ="like_button_label" > < / div >
    #
    #     < div
    #
    #     class ="like_button_count" > 87 < / div >
    #
    #     < span
    #
    #     class ="blind_label" > Нравится < / span >
    #
    # < / a >
    #     self.

    def open_page_and_write_message(self, recipient_vk_id, message):
        print(self.message_page_url.format(recipient_vk_id))
        self.chrome_browser.get(self.message_page_url.format(recipient_vk_id))
        xpath_for_evaluating_when_user_last_autorized = \
            '//*[@id="content"]/div/div[1]/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/span[2]'
        elem_for_evaluating_when_user_last_autorized = \
            self.chrome_browser.find_element_by_xpath(xpath_for_evaluating_when_user_last_autorized)
        old_years = ['2018', '2017', '2016']
        for year in old_years:
            if elem_for_evaluating_when_user_last_autorized.text.find(year) is not -1:
                raise TooFarLastAutorisationException

        # xpath_for_elem_for_add_some_data_which_is_not_need = ''
        # elem_for_add_some_data_which_is_not_need = \
        #     self.chrome_browser.find_element_by_xpath(xpath_for_elem_for_add_some_data_which_is_not_need)
        # if elem_for_add_some_data_which_is_not_need:
        #     elem_for_add_some_data_which_is_not_need.click()
        self.chrome_browser.switch_to.parent_frame()

        try:
            time.sleep(1)
            logging.info("HERE")
            xpath_for_closing_window_for_page_confirm = '//*[@id="box_layer"]/div[2]/div/div[1]/div[1]'
            elem_for_closing_window_for_page_confirm = \
                self.chrome_browser.find_element_by_xpath(xpath_for_closing_window_for_page_confirm)
            elem_for_closing_window_for_page_confirm.click()
            logging.info("{} - closed confirm popup", recipient_vk_id)
        except Exception as n_ex:
            logging.info("{} - haven't found elem_for_closing_window_for_page_confirm", recipient_vk_id)
        try:
            time.sleep(1)
            xpath_for_closing_window_about_notification_possibility = '//*[@id="box_layer"]/div[2]/div/div[2]/button'
            elem_for_closing_window_about_notification_possibility = \
                self.chrome_browser.find_element_by_xpath(xpath_for_closing_window_about_notification_possibility)
            elem_for_closing_window_about_notification_possibility.click()
        except Exception as n_ex:
            logging.info("{} - haven't found elem_for_closing_window_about_notification_possibility", recipient_vk_id)

        elem_for_input_message = self.chrome_browser.find_element_by_id("im_editable{}".format(recipient_vk_id))
        print(elem_for_input_message)
        elem_for_input_message.send_keys(message.format("Товарищ"))
        time.sleep(2)
        # xpath_for_adding_item = '// *[ @ id = "content"] / div / div[1] / div[3] / div[2] / div[4] / div[3] / div[4] / div[1] / div[2] / div / div / a / span'
        xpath_for_adding_item = '// *[ @ id = "content"] / div / div[1] / div[3] / div[2] / div[4] / div[2] / div[4] / div[1] / div[2] / div / div / a / span'

        elem_for_adding_item = self.chrome_browser.find_element_by_xpath(xpath_for_adding_item)
        elem_for_adding_item.click()
        time.sleep(2)

        #xpath_for_choosing_audio = '// *[ @ id = "content"] / div / div[1] / div[3] / div[2] / div[4] / div[3] / div[4] / div[1] / div[2] / div / div / div / div / a[3]'
        #xpath_for_choosing_audio = '// *[ @ id = "content"] / div / div[1] / div[3] / div[2] / div[4] / div[2] / div[4] / div[1] / div[2] / div / div / div / div / a[3]'
        xpath_for_choosing_audio = '//*[@id="content"]/div/div[1]/div[3]/div[2]/div[4]/div[2]/div[4]/div[1]/div[2]/div/div/div/div/a[3]'

        elem_for_choosing_audio = self.chrome_browser.find_element_by_xpath(xpath_for_choosing_audio)
        elem_for_choosing_audio.click()
        time.sleep(2)
        selector_for_applying_audio = "document.querySelector('#box_layer > div.popup_box_container > div > div.box_body > div > div.ape_item_list._ape_item_list.noselect > div:nth-child(1) > div.ape_attach')"
        track_id = '406533617_456239027'

        # elem_for_for_applying_audio = self.chrome_browser.find_element_by_xpath('//*[@id="box_layer"]/div[2]/div/div[2]/div/div[5]/div[1]/div[1]')
        elem_for_for_applying_audio = self.chrome_browser.find_element_by_xpath(
            '// *[ @ id = "box_layer"] / div[2] / div / div[2] / div / div[3] / div[1] / div[1]')
        # print(elem_for_for_applying_audio)
        elem_for_for_applying_audio.click()
        time.sleep(2)

        selector = '# content > div > div.im-page.js-im-page.im-page_classic.im-page_history-show > div.im-page--history.page_block._im_page_history.im-page--history_empty-hist > div.im-page-history-w > div.im-page--chat-input._im_chat_input_w > div.im-chat-input.clear_fix.im-chat-input_classic._im_chat_input_parent > div.im-chat-input--textarea.fl_l._im_text_input._emoji_field_wrap._voice_field_wrap > div.im-chat-input--txt-wrap._im_text_wrap > button'
        #xpath_for_send_message = '//*[@id="content"]/div/div[1]/div[3]/div[2]/div[4]/div[3]/div[4]/div[1]/button'
        xpath_for_send_message = '//*[@id="content"]/div/div[1]/div[3]/div[2]/div[4]/div[2]/div[4]/div[1]/button'
        button_class_element = self.chrome_browser.find_element_by_xpath(xpath_for_send_message)
        button_class_element.click()
        time.sleep(5)
        self.chrome_browser.close()
        time.sleep(SeleniumSender.sleep_time)
