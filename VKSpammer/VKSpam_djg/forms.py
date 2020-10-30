#!/usr/bin/env python3
# -*- coding: utf8 -*-
__author__ = 'grishaev'

from django import forms
from .models import *
from django.forms.widgets import RadioSelect
# from django.utils.translation import ugettext as _


class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)


class CampParamsForm(forms.ModelForm):

    class Meta:
        # model = CampParams
        # fields = ('title', 'start_date', 'service_id', 'plug')
        fields = '__all__'
        widgets = {
            'title': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
            'start_date' : forms.DateTimeInput,
        }

    def save(self, user):
        obj = super(CampParams, self).save(commit=False)
        obj.customer = user
        return obj.save()


class UploadFileForm(forms.Form):

    # костыльный хард код
    # здесь нужно в CHOICES указать None или пустую строку, чтобы обрабатывалось корректно незаданная кампания
    CHOICES = [(None,'Не задано')]
    for i in range(10):
         CHOICES.append((i, str(i) + '  ' + str(i)))
    CHOICES = tuple(CHOICES)
    file = forms.FileField(label='Файл',  required=True)
    campaign_id = forms.ChoiceField(
        label='Название кампании', required=True, choices=CHOICES,
    )


class ChoiceGroupForm(forms.Form):
    """
    Класс-родитель для форм, в которых есть поле для выбора группы
    """
    CHOICES = [(None,'Не задано')]
    for obj in VkGroupUserUnion2.objects.distinct('vk_group_id'):
        CHOICES.append((obj.vk_group_id, 'группа ' + str(obj.vk_group_id)))
    vk_group_id = forms.ChoiceField(
            label='Идентификатор группы', required=True, choices=CHOICES,
    )

    BOTS_CHOICES = [(None, 'Не задано')]
    for bot in BotsSenders.objects.all():
        BOTS_CHOICES.append((str(bot.vk_user_id), bot.surname))

    bots_senders = forms.ChoiceField(
        label='Коммуникатор Бот', choices=BOTS_CHOICES, required=False
    )

    is_autocaptcha = forms.BooleanField(label='Авторазбор капчи', required=False)
    is_sex_considered = forms.BooleanField(label='Рассылка с учётом пола', required=False)
    is_multitext = forms.BooleanField(label='Включить мультитекст', required=False)


class GetTokenForm(forms.Form):

    # class Meta:
        # model = CampParams
        # fields = ('title', 'start_date', 'service_id', 'plug')
        # fields = '__all__'
        # widgets = {
            # 'user_token': forms.CharField(),
        # }

    user_token = forms.URLField(label='Введите токен-строку', required=True)


class AskTokenForm(forms.Form):

    ask_token_btn = forms.HiddenInput(attrs={'take_token': 'True'},)
    rend_res = ask_token_btn.render('take_token', 'True')
    text = 'Получить токен принудительно'


class DoCommentPhotoForm(ChoiceGroupForm):

    # todo выбираем группы дистинктом! Переделать на выборку из таблицы, содержащей группы!
    # CHOICES = [(None,'Не задано')]
    # for obj in VkGroupUserUnion.objects.distinct('vk_group_id'):
    #    CHOICES.append((obj.vk_group_id, 'группа ' + str(obj.vk_group_id)))
    # vk_group_id = forms.ChoiceField(
    #    label='Идентификатор группы', required=True, choices=CHOICES,
    # )
    message = forms.CharField(initial='{}, !!))', widget=forms.Textarea(attrs={
        'cols': 20,
        'rows': 10,
        'title':'text',
        # 'placeholder': '{}, !!))'
        }
    ))
    # captcha = forms.CharField(widget=forms.TextInput)
    status_for_start_of_posting_ava_comment = 'начали постинг комменнтов к аватаркам'
    status_for_finish_of_posting_ava_comment = 'закончили постинг комментов к аватаркам'
    campaign_id = None


class DoCommentPhotoMultisenderForm(ChoiceGroupForm):

    status_for_start_of_multisender_posting_ava_comment = 'начали постинг комменнтов к аватаркам в режиме мультисендер'
    status_for_finish_of_multisender_posting_ava_comment = \
        'закончили постинг комментов к аватаркам в режиме мультисендер'
    campaign_id = None
    BOTS_CHOICES = None
    bots_senders = None
    is_autocaptcha = None
    is_sex_considered = None
    is_multitext = None


class DoCommentPhotoMustiprocMultisendForm(forms.Form):

    # vk_group_id_for_multiproc = vk_group_id
    CHOICES_MULT_MULT = [(None,'Не задано')]
    for obj in VkGroupUserUnion2.objects.distinct('vk_group_id'):
        CHOICES_MULT_MULT.append((obj.vk_group_id, 'группа ' + str(obj.vk_group_id)))
    vk_group_id_for_mp = forms.ChoiceField(
            label='Идентификатор группы', required=True, choices=CHOICES_MULT_MULT,
    )

    status_for_start_of_mpost_msend_posting_ava_comment = 'начали постинг комменнтов к аватаркам в режиме мультисендер'
    status_for_finish_of_mpost_msend_posting_ava_comment = 'закончили постинг комментов к аватаркам в режиме мультисендер'
    campaign_id = None
    BOTS_CHOICES = None
    bots_senders = None
    is_autocaptcha = None
    is_sex_considered = forms.BooleanField(label='Рассылка с учётом пола', required=False)
    is_multitext = None


class DoPrivatMessageForm(forms.Form):

    # todo выбираем группы дистинктом! Переделать на выборку из таблицы, содержащей группы!
    CHOICES_2 = [(None, 'Не задано')]
    for obj in VkGroupUserUnion2.objects.distinct('vk_group_id'):
        CHOICES_2.append((obj.vk_group_id, 'группа ' + str(obj.vk_group_id)))
    vk_group_id_2 = forms.ChoiceField(
        label='Идентификатор группы', required=True, choices=CHOICES_2,
    )
    # privat_message = forms.CharField(widget=forms.Textarea(attrs={
        # 'cols': 35, 'rows': 7, 'title':'text', }))
    status_for_start_of_sending_privat_messages = 'начали отправку сообщений в личку'
    status_for_finish_of_sending_privat_messages = 'закончили отправку сообщений в личку'


class SendMessagesToFriendsPrivateForm(forms.Form):

    VK_SENDERS = [(None, 'Не задано')]

    for bot in BotsSenders.objects.all():
        if not bot.is_blocked:
            VK_SENDERS.append((str(bot.vk_user_id), str(bot.surname)))
    vk_senders = forms.ChoiceField(
        label='Коммуникатор Бот', choices=VK_SENDERS, required=False
    )

    is_autocaptcha = forms.BooleanField(label='Авторазбор капчи', required=False)
    is_sex_considered = forms.BooleanField(label='Рассылка с учётом пола', required=False)
    is_multitext = forms.BooleanField(label='Включить мультитекст', required=False)


class SendMessagesToAimGroupUserForm(forms.Form):

    # VK_SENDERS = [(None, 'Не задано')]

    # for bot in BotsSenders.objects.all():
    #     if not bot.is_blocked:
    #         VK_SENDERS.append((str(bot.vk_user_id), str(bot.surname)))
    # vk_senders = forms.ChoiceField(
    #     label='Коммуникатор Бот', choices=VK_SENDERS, required=False
    # )
    status_of_sending_privat_messages = 'Какой-то там статус'
    start_sender_id = forms.IntegerField(label='id сендера, с которого стартовать', required=True)
    is_multiprocessing = forms.BooleanField(label='Включить режим мультипроцессинга', required=False)
    is_sex_considered = forms.BooleanField(label='Рассылка с учётом пола', required=False)
    is_multitext = forms.BooleanField(label='Включить мультитекст', required=False)


class DoPrivatMultisenderSendingMessForm(forms.Form):

    # todo выбираем группы дистинктом! Переделать на выборку из таблицы, содержащей группы!
    CHOICES_2 = [(None, 'Не задано')]
    for obj in VkGroupUserUnion2.objects.distinct('vk_group_id'):
        CHOICES_2.append((obj.vk_group_id, 'группа ' + str(obj.vk_group_id)))
    vk_group_id_multisender = forms.ChoiceField(
        label='Идентификатор группы', required=True, choices=CHOICES_2,
    )

    status_for_start_of_sending_privat_messages = 'начали отправку сообщений в личку в режиме "Мультисендер"'
    status_for_finish_of_sending_privat_messages = 'закончили отправку сообщений в личку в режиме "Мультесендер"'


class MakeDistributionThroughFakeBrowserForm(forms.Form):

    # todo выбираем группы дистинктом! Переделать на выборку из таблицы, содержащей группы!
    CHOICES_2 = [(None, 'Не задано')]
    for obj in VkGroupUserUnion2.objects.distinct('vk_group_id'):
        CHOICES_2.append((obj.vk_group_id, 'группа ' + str(obj.vk_group_id)))
    vk_group_id_multisender = forms.ChoiceField(
        label='Идентификатор группы', required=True, choices=CHOICES_2,
    )

    is_sex_considered = forms.BooleanField(label='Рассылка с учётом пола', required=False)
    is_multitext = forms.BooleanField(label='Включить мультитекст', required=False)

    status_for_start_of_sending_privat_messages = \
        'начали отправку сообщений в личку в режиме "Мультисендер"'
    status_for_finish_of_sending_privat_messages = \
        'закончили отправку сообщений в личку в режиме "Мультесендер"'


class DoWallPostForm(ChoiceGroupForm):

    wall_post = forms.CharField(widget=forms.Textarea(attrs={
                'cols': 35, 'rows': 7, 'title': 'text', }))
    status_for_start_of_wall_post = 'начали отправку постов на стену'
    status_for_finish_of_wall_post = 'закончили отправку постов на стену'

    class Media:
        css = {
            'all': ('style.css',)
        }


class EnterGroupIdForm(forms.Form):

    inputed_group_id = forms.CharField(label='Введите id группы', widget=forms.TextInput(), required=True)
    status_for_getting_subscribers = 'успешно обработали группу:{} и добавили данные по пользователям в БД'


class EnterCaptchaForm(forms.Form):

    inputed_captcha = forms.CharField(label='Введите каптчу', widget=forms.TextInput(), required=True)
    kind_of_distribution = forms.BooleanField(label='Рассылка по стенам?', required=False)
    captcha_inf = 'успешно обработали капчу: {} и отправили несколько постов'


class GetStatisticsForm(forms.Form):

    # todo выбираем группы дистинктом! Переделать на выборку из таблицы, содержащей группы!
    CHOICES_3 = [(None, 'Не задано')]
    for obj in VkGroupUserUnion2.objects.distinct('vk_group_id'):
        CHOICES_3.append((obj.vk_group_id, 'группа ' + str(obj.vk_group_id)))
    # todo Чойсы должны быть большими буквами. Переделать!
    vk_group_id_3 = forms.ChoiceField(
        label='Идентификатор группы', required=True, choices=CHOICES_3,
    )
    CHOICES_FOR_KIND_OF_SENDING = [
        # (1,'Статистика по комментам аватарок'),
        # (2, 'Статистика по сообщениям в личку'),
        # (3, 'Общее количество пользователей группы, имеющееся в БД'),
        (4, 'Получить доступную статистику по группе')
    ]
    CHOICES_FOR_KIND_OF_SENDING = forms.ChoiceField(
        widget=RadioSelect,
        required=True,
        choices=CHOICES_FOR_KIND_OF_SENDING)


class GetAvaInfoAndPhotoSettingsForm(ChoiceGroupForm):

    is_autocaptcha = None
    bots_senders = None
    is_sex_considered = None
    status_for_start_of_getting_photo_settings = 'начали получение настроек аватарок'
    status_for_finish_of_getting_photo_settings = 'закончили получение настроек аватарок'


class MultisenderGetAvaInfoAndPhotoSettingForm(forms.Form):

    CHOICES_for_multisender_g_a_i_a_p_s_f = [(None,'Не задано')]
    for obj in VkGroupUserUnion2.objects.distinct('vk_group_id'):
        CHOICES_for_multisender_g_a_i_a_p_s_f.append((obj.vk_group_id, 'группа ' + str(obj.vk_group_id)))
    vk_group_id_multisender_g_a_i_a_p_s_f = forms.ChoiceField(
            label='Идентификатор группы', required=True, choices=CHOICES_for_multisender_g_a_i_a_p_s_f,
    )
    is_autocaptcha = None
    bots_senders = None
    is_sex_considered = None
    status_for_start_of_getting_photo_settings = 'начали получение настроек аватарок'
    status_for_finish_of_getting_photo_settings = 'закончили получение настроек аватарок'


class GetSetOfTokensForm(forms.Form):

    ask_set_of_token_btn = forms.HiddenInput(attrs={'take_set_of_token' : 'True'},)
    rend_res = ask_set_of_token_btn.render('ask_set_of_token_btn', 'True')
    text = 'Получить токены для множества пользователей'
    finish_of_getting_tokens = 'Получение токенов для множества пользователей закончено'


class AddBotsInEachOtherFriendForm(forms.Form):

    add_bots_to_eachother_friend_btn = forms.HiddenInput(attrs={'take_set_of_token': 'True'}, )
    __rend_res = add_bots_to_eachother_friend_btn.render('add_bots_to_eachother_friend_btn', 'True')
    __text = 'Добавить сендеров во взаимные друзья'
    finish_of_adding_bots_to_friends = 'Добавление сендеров во взаимные друзья закончено'


class AutorisationForm(forms.Form):
    autorisation = forms.HiddenInput(attrs={'autorisation': 'True'},)
    rend_res = autorisation.render('autorisation', 'True')


class GetUpdatesOfAimGroupForm(forms.Form):

    get_updates_btn = forms.HiddenInput(attrs={'get_updates': 'True'},)
    rend_res_of_getting_updates = get_updates_btn.render('get_updates_btn ', 'True')


class GetAimGroupWallPostsForm(forms.Form):

    get_updates_btn = forms.HiddenInput(attrs={'get_updates': 'True'},)
    rend_res_of_getting_updates = get_updates_btn.render('get_updates_btn ', 'True')


class LikeAimGroupPostsForm(forms.Form):
    CHOICES_for_aim_group_posts_form = [(None, 'Не задано')]
    for obj in VkWallPosts.objects.all():
        CHOICES_for_aim_group_posts_form.append((obj.vk_wall_post_id, 'пост: ' + str(obj.vk_wall_post_id)))

    vk_wall_post_id = forms.ChoiceField(
        label='Идентификатор поста',
        required=True,
        choices=CHOICES_for_aim_group_posts_form
    )
