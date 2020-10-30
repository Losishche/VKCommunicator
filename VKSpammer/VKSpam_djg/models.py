#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
# * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models

import django.dispatch
from django.contrib.postgres.fields import ArrayField
# from django.dispatch import receiver
# from django.contrib import admin # для обновления админки при создании кампаний
# from django.db.models import signals


handler_captcha = django.dispatch.Signal(providing_args=["state"])
# class exp(models.Model):
# id = models.IntegerField(primary_key=True)
# vk_experiment = models.BigIntegerField(blank=True, null=True)


class VkGroupUser(models.Model):

    id = models.IntegerField(primary_key=True)
    vk_id = models.BigIntegerField(blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True)
    first_name = models.CharField(max_length=60, blank=True)
    can_write_private_message = models.IntegerField(blank=True, null=True)
    have_sent_messages = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'vk_group_user'


class VkGroupUserUnion2(models.Model):

    id = models.AutoField(primary_key=True)  # AutoField?
    vk_id = models.BigIntegerField(blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True)
    first_name = models.CharField(max_length=80, blank=True)
    can_write_private_message = models.IntegerField(blank=True, null=True)
    have_sent_messages = models.NullBooleanField()
    have_post_photo_comment = models.NullBooleanField()
    vk_group_id = models.CharField(max_length=80, blank=True)
    avatar_id = models.IntegerField(blank=True, null=True)
    can_post_ava_comment = models.NullBooleanField()
    sex = models.CharField(max_length=1, blank=True)
    bdate = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    added_to_friends = models.NullBooleanField(null=True)
    have_post_wall_comment = models.NullBooleanField()

    class Meta:
        # если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'vk_group_user_union_2'

    def __str__(self):
        vk_user = '{}, {}, {}, {}'.format(self.id, self.vk_id, self.last_name, self.first_name)
        return vk_user


class VkGroupUserUnion(models.Model):

    id = models.AutoField(primary_key=True)  # AutoField?
    vk_id = models.BigIntegerField(blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True)
    first_name = models.CharField(max_length=80, blank=True)
    can_write_private_message = models.IntegerField(blank=True, null=True)
    have_sent_messages = models.NullBooleanField()
    have_post_photo_comment = models.NullBooleanField()
    vk_group_id = models.CharField(max_length=80, blank=True)
    avatar_id = models.IntegerField(blank=True, null=True)
    can_post_ava_comment = models.NullBooleanField()
    sex = models.CharField(max_length=1, blank=True)
    bdate = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=30, blank=True)
    added_to_friends = models.NullBooleanField(null=True)
    have_post_wall_comment = models.NullBooleanField()

    class Meta:
        # если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'vk_group_user_union'

    def __str__(self):
        vk_user = '{}, {}, {}, {}'.format(self.id, self.vk_id, self.last_name, self.first_name)
        return vk_user

    # def get_vk_groups_id(self):
    #     return


class GorkiyGroupUser(models.Model):

    id = models.AutoField(primary_key=True)  # AutoField?
    vk_id = models.BigIntegerField(blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True)
    first_name = models.CharField(max_length=80, blank=True)
    can_write_private_message = models.IntegerField(blank=True, null=True)
    can_post_ava_comment = models.IntegerField(blank=True, null=True)
    count_sent_privat_messages = models.IntegerField(blank=True, null=True)
    count_posted_photo_comment = models.IntegerField(blank=True, null=True)
    count_bots_added_to_friends = models.IntegerField(blank=True, null=True)
    count_posted_wall_comment = models.IntegerField(blank=True, null=True)
    count_of_friends = models.IntegerField(blank=True, null=True)
    count_of_messaged_friends = models.IntegerField(blank=True, null=True)
    avatar_id = models.IntegerField(blank=True, null=True)
    sex = models.CharField(max_length=1, blank=True)
    bdate = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    have_sent_invite_private_message = models.NullBooleanField()

    class Meta:
        # если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'gorkiy_group_user'

    def __str__(self):
        vk_user = '{}, {}, {}, {}'.format(self.id, self.vk_id, self.last_name, self.first_name)
        return vk_user


class CampParams(models.Model):

    id = models.AutoField(primary_key=True)
    camp_name = models.CharField(max_length=100)
    vk_group_user_tb = models.CharField(max_length=40)
    is_considered_user_sex = models.BooleanField()
    # ava_text = models.CharField(max_length=80, blank=True)
    # private_text = models.CharField(max_length=120, blank=True)
    # wall_text = models.CharField(max_length=120, blank=True)
    ava_attach = ArrayField(
            models.CharField(max_length=35, blank=True),
            size=6,
            )  # If passed, the array will have a maximum size as specified.
    ava_attach_woman = ArrayField(
            models.CharField(max_length=35, blank=True),
            size=6,
            )  # If passed, the array will have a maximum size as specified.
    private_attach = ArrayField(
            models.CharField(max_length=35, blank=True),
            size=6,
            )  # If passed, the array will have a maximum size as specified.
    wall_attach = ArrayField(
            models.CharField(max_length=35, blank=True),
            size=6,
            )  # If passed, the array will have a maximum size as specified.
    send_to_ava = models.BooleanField()
    send_to_private = models.BooleanField()
    send_to_wall = models.BooleanField()
    is_daily = models.BooleanField()
    daily_start_date = models.DateTimeField(blank=True, null=True)
    ORDER_OF_DISTR_CHOICES = (
        (1, 'Wall-Ava'),
        (2, 'Wall-Ava-Privat'),
        (3, 'Ava-Wall'),
        (4, 'Ava-Wall-Privat')
    )
    order_of_distr = models.IntegerField(null=True, choices=ORDER_OF_DISTR_CHOICES)
    delay_between_posts = models.IntegerField(default=3, null=False)

    class Meta:
        managed = True
        db_table = 'camp_params'
    '''
    @classmethod
    def create_model(cls, app_label='VKSpam_djg', module='', options=None, admin_opts=None):
        """
        Create specified model
        """

        name = 'VkGroupUserUnion_{}'.format(cls.id)
        class Meta:
            # Using type('Meta', ...) gives a dictproxy error during model creation
            pass

        if app_label:
            # app_label must be set using the Meta inner class
            setattr(Meta, 'app_label', app_label)

        # Update Meta with any options that were provided
        if options is not None:
            for key, value in options.iteritems():
                setattr(Meta, key, value)

        # Set up a dictionary to simulate declarations within a class
        attrs = {'__module__': module, 'Meta': Meta}

        # Add in any fields that were provided
        #if fields:
        #    attrs.update(fields)

        # Create the class, which automatically triggers ModelBase processing
        model = type(name, (models.Model, ), attrs)

        # Create an Admin class if admin options were provided
        if admin_opts is not None:
            class Admin(admin.ModelAdmin):
                pass
            for key, value in admin_opts:
                setattr(Admin, key, value)
            admin.site.register(model, Admin)

        return model'''


class VkWallPosts(models.Model):

    id = models.AutoField(primary_key=True)
    vk_wall_post_id = models.IntegerField(null=False)
    owner_id = models.IntegerField(null=False)
    vk_json_post_parameters = models.CharField(max_length=2000, blank=True)

    class Meta:
        managed = True
        db_table = 'vk_wall_post_params'

    def __str__(self):
        vk_wall_post_params = str(self.id) + ': ' + \
                              str(self.vk_wall_post_id) + ', ' + \
                              str(self.vk_json_post_parameters)
        return vk_wall_post_params


class VkAudioParams(models.Model):

    id = models.AutoField(primary_key=True)
    vk_audio_id = models.CharField(max_length=150, blank=False)
    audio_title = models.CharField(max_length=300, blank=True)
    audio_perfomer_title = models.CharField(max_length=200, blank=True)

    class Meta:
        managed = True
        db_table = 'vk_audio_params'

    def __str__(self):
        vk_audio_param = str(self.id) + ': ' + str(self.vk_audio_id) + ', ' + str(self.audio_title)
        return vk_audio_param


class PrivateMessages(models.Model):

    id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=100, blank=True)
    camp_id = models.ForeignKey(CampParams, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'privat_messages'

    def __str__(self):
        privat_mess = str(self.id) + ': ' + str(self.message)
        return privat_mess


class InvitePrivateMessages(models.Model):

    id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=150, blank=True)
    camp_id = models.ForeignKey(CampParams, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'invite_private_messages'

    def __str__(self):
        invite_private_messages = str(self.id) + ': ' + str(self.message)
        return invite_private_messages


class AvaMessages(models.Model):

    id = models.AutoField(primary_key=True)
    ava_message = models.CharField(max_length=100, blank=True)
    camp_id = models.ForeignKey(CampParams, on_delete=models.CASCADE)

    class Meta:
        # если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'ava_messages'

    def __str__(self):
        ava_mess = str(self.id) + ': ' + str(self.ava_message)
        return ava_mess


class InviteMessagesToLoyalGroupUsers(models.Model):

    id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=150, blank=True)
    camp_id = models.ForeignKey(CampParams, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'invite_messages_to_loyal_group_users'

    def __str__(self):
        invite_messages_to_loyal_group_users = str(self.id) + ': ' + str(self.message)
        return invite_messages_to_loyal_group_users


class VKApplications(models.Model):

    id = models.AutoField(primary_key=True)
    vk_app_id = models.IntegerField(null=False)
    vk_app_name = models.CharField(max_length=20, null=False)
    vk_protected_key = models.CharField(max_length=30, null=False)

    class Meta:
        # если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'vk_applications'

    def __str__(self):

        vk_applic_info = str(self.vk_app_name) + ', защищённый ключ: ' + str(self.vk_protected_key)
        return vk_applic_info


class BotsSenders(models.Model):

    id = models.AutoField(primary_key=True)
    vk_user_id = models.IntegerField(null=False)
    name = models.CharField(max_length=20, null=False)
    surname = models.CharField(max_length=40, null=False)
    vk_login = models.CharField(max_length=35, null=False)
    vk_password = models.CharField(max_length=20, null=False)
    vk_token = models.CharField(max_length=100, null=True, blank=True)
    vk_token_expired = models.DateTimeField(null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    day_sent_message_count = models.IntegerField(null=False, default=0)
    date_of_starting_day_counting = models.DateTimeField(null=True, blank=True)
    # is_blocked_forever = models.BooleanField(default=False)

    def __str__(self):
        bot_sender = '{}, {}, {}, {}, {}'.format(self.id, self.vk_user_id, self.name, self.surname, self.vk_login)
        return bot_sender

    class Meta:
        # если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'bots_senders'


class BotsFriends(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    vk_user_id = models.BigIntegerField(blank=True, null=True)
    friend_bot = models.ForeignKey(BotsSenders, on_delete=models.CASCADE)
    last_name = models.CharField(max_length=80, blank=True)
    first_name = models.CharField(max_length=80, blank=True)
    can_post_ava_comment = models.IntegerField(blank=True, null=True)
    have_sent_invite_private_messages = models.NullBooleanField(default=False)
    count_sent_private_messages = models.IntegerField(blank=True, null=True)
    count_posted_photo_comment = models.IntegerField(blank=True, null=True)
    count_posted_wall_comment = models.IntegerField(blank=True, null=True)
    count_of_friends = models.IntegerField(blank=True, null=True)
    count_of_messaged_friends = models.IntegerField(blank=True, null=True)
    avatar_id = models.IntegerField(blank=True, null=True)
    sex = models.CharField(max_length=1, blank=True)
    bdate = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        # если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'bots_friend'

    def __str__(self):
        vk_user = '{}, {}, {}, {}, {}'.format(self.id, self.vk_user_id, self.last_name, self.friend_bot, self.first_name)
        return vk_user


class VkErrorText(models.Model):

    id = models.AutoField(primary_key=True)
    vk_error_code = models.IntegerField(null=True, blank=True)
    text = models.CharField(max_length=120, null=False)

    def __str__(self):

        vk_err_text = '{}, {}'.format(self.vk_error_code, self.text)
        return vk_err_text

    class Meta:
        managed = True
        db_table = 'vk_error_text'


class OkBotsSenders(models.Model):

    id = models.AutoField(primary_key=True)
    ok_user_id = models.BigIntegerField(null=False)
    name = models.CharField(max_length=20, null=False)
    surname = models.CharField(max_length=40, null=False)
    ok_login = models.CharField(max_length=35, null=False)
    ok_password = models.CharField(max_length=20, null=False)
    ok_token = models.CharField(max_length=100, null=True, blank=True)
    ok_token_expired = models.DateTimeField(null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    day_sent_message_count = models.IntegerField(null=False, default=0)
    date_of_starting_day_counting = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        ok_bot_sender = '{}, {}, {}, {}'.format(self.ok_user_id, self.name, self.surname, self.ok_login)
        return ok_bot_sender

    class Meta:
        # если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'ok_bots_senders'


class OkGroups(models.Model):

    id = models.AutoField(primary_key=True)
    ok_group_id = models.CharField(max_length=80, blank=True)
    ok_public_group_name = models.CharField(max_length=150, blank=True,  null=True)

    class Meta:
        managed = True
        db_table = 'ok_groups'


class OkGroupUserUnion(models.Model):

    id = models.AutoField(primary_key=True)
    ok_id = models.BigIntegerField(blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=80, blank=True, null=True)
    can_write_private_message = models.IntegerField(null=True)
    have_sent_messages = models.NullBooleanField()
    have_post_photo_comment = models.NullBooleanField()
    ok_group_id = models.CharField(max_length=80, blank=True)
    ok_avatar_id = models.BigIntegerField(blank=True, null=True)
    can_post_ava_comment = models.NullBooleanField()
    sex = models.CharField(max_length=6, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=230, blank=True, null=True)
    added_to_friends = models.NullBooleanField(null=True)
    have_post_wall_comment = models.NullBooleanField()

    class Meta:
        # если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'ok_group_user_union'

    def __str__(self):
        vk_user = '{}, {}, {}, {}'.format(self.id, self.ok_id, self.last_name, self.first_name)
        return vk_user

    # def get_ok_groups_id(self):
    #     return

    '''
    id = models.AutoField(primary_key=True)  # AutoField?
    vk_id = models.BigIntegerField(blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True)
    first_name = models.CharField(max_length=80, blank=True)
    can_write_private_message = models.IntegerField(blank=True, null=True)
    have_sent_messages = models.NullBooleanField()
    have_post_photo_comment = models.NullBooleanField()
    vk_group_id = models.CharField(max_length=80, blank=True)
    avatar_id = models.IntegerField(blank=True, null=True)
    can_post_ava_comment = models.NullBooleanField()
    sex = models.CharField(max_length=1, blank=True)
    bdate = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=30, blank=True)
    added_to_friends = models.NullBooleanField(null=True)
    have_post_wall_comment = models.NullBooleanField()
    '''

"""
def create_new_tab_by_signal(sender, instance, created, **kwargs):
    '''Создаёт новую таблицу для кампании'''
    if created:
       subject = 'New campaign created'
       sender.create_model()

signals.post_save.connect(create_new_tab_by_signal, sender=CampParams)
"""
