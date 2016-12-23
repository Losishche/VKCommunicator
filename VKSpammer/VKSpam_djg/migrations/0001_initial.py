# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VkGroupUser',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('vk_id', models.BigIntegerField(null=True, blank=True)),
                ('last_name', models.CharField(max_length=80, blank=True)),
                ('first_name', models.CharField(max_length=60, blank=True)),
                ('can_write_private_message', models.IntegerField(null=True, blank=True)),
                ('have_sent_messages', models.NullBooleanField()),
            ],
            options={
                'db_table': 'vk_group_user',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VkGroupUserUnion',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('vk_id', models.BigIntegerField(null=True, blank=True)),
                ('last_name', models.CharField(max_length=80, blank=True)),
                ('first_name', models.CharField(max_length=80, blank=True)),
                ('can_write_private_message', models.IntegerField(null=True, blank=True)),
                ('have_sent_messages', models.NullBooleanField()),
                ('have_post_photo_comment', models.NullBooleanField()),
                ('vk_group_id', models.CharField(max_length=80, blank=True)),
                ('avatar_id', models.IntegerField(null=True, blank=True)),
                ('can_post_ava_comment', models.NullBooleanField()),
                ('sex', models.CharField(max_length=1, blank=True)),
                ('bdate', models.DateField(null=True, blank=True)),
                ('city', models.CharField(max_length=30, blank=True)),
                ('added_to_friends', models.NullBooleanField()),
            ],
            options={
                'db_table': 'vk_group_user_union',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
