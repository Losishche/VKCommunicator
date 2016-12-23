# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0015_campparams_order_of_distr'),
    ]

    operations = [
        migrations.CreateModel(
            name='BotsSenders',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('vk_user_id', models.IntegerField()),
                ('name', models.CharField(max_length=20)),
                ('surname', models.CharField(max_length=40)),
                ('vk_login', models.CharField(max_length=35)),
                ('vk_password', models.CharField(max_length=20)),
                ('vk_token', models.CharField(null=True, max_length=60)),
                ('vk_token_expired', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'bots_senders',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='campparams',
            name='delay_between_posts',
            field=models.IntegerField(default=3),
        ),
    ]
