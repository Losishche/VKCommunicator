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
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

handler_captcha = django.dispatch.Signal(providing_args=["state"])
#class exp(models.Model):
#id = models.IntegerField(primary_key=True)
#vk_experiment = models.BigIntegerField(blank=True, null=True)

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
        #если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'vk_group_user_union'

    def __str__(self):
        vk_user = '{}, {}, {}, {}'.format(self.id, self.vk_id, self.last_name, self.first_name)
        return vk_user

    def get_vk_groups_id(self):
        return


class CampParams(models.Model):

    id = models.AutoField(primary_key=True)
    is_considered_user_sex = models.BooleanField()
    ava_text = models.CharField(max_length=80, blank=True)
    private_text = models.CharField(max_length=120, blank=True)
    wall_text = models.CharField(max_length=120, blank=True)
    ava_attach = ArrayField(
            models.CharField(max_length=35, blank=True),
            size=6,
            ) #If passed, the array will have a maximum size as specified.
    ava_attach_woman = ArrayField(
            models.CharField(max_length=35, blank=True),
            size=6,
            ) #If passed, the array will have a maximum size as specified.
    private_attach = ArrayField(
            models.CharField(max_length=35, blank=True),
            size=6,
            ) #If passed, the array will have a maximum size as specified.
    wall_attach = ArrayField(
            models.CharField(max_length=35, blank=True),
            size=6,
            ) #If passed, the array will have a maximum size as specified.
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
    order_of_distr = models.IntegerField(null=True, choices = ORDER_OF_DISTR_CHOICES)
    delay_between_posts = models.IntegerField(default=3, null=False)

    class Meta:
        #если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'camp_params'



class PrivatMessages(models.Model):

    id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=100, blank=True)

    class Meta:
        #если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'privat_messages'

    def __str__(self):

        privat_mess = str(self.id) +': ' + str(self.message)
        return privat_mess



class AvaMessages(models.Model):

    id = models.AutoField(primary_key=True)
    ava_message = models.CharField(max_length=100, blank=True)

    class Meta:
        #если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'ava_messages'

    def __str__(self):

        ava_mess = str(self.id) +': ' + str(self.ava_message)
        return ava_mess



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

    def __str__(self):

        bot_sender = '{}, {}, {}, {}'.format(self.vk_user_id, self.name, self.surname, self.vk_login)
        return bot_sender


    class Meta:
        #если managed=False, миграции не работают для данной таблицы
        managed = True
        db_table = 'bots_senders'


class VkErrorText(models.Model):

    id = models.AutoField(primary_key=True)
    vk_error_code = models.IntegerField(null=True, blank=True)
    text = models.CharField(max_length=120, null=False)

    def __str__(self):

        vk_err_text = '{}, {}'.format(self.vk_error_code, self.text)
        return vk_err_text

    class Meta:

        managed= True
        db_table = 'vk_error_text'

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
class TestTable(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    some_field = models.CharField(max_length=80, null=True)
    some_field2 = models.CharField(max_length=80, null=True)