# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0018_botssenders_is_blocked'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivatMessages',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('message', models.CharField(max_length=35, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'privat_messages',
            },
        ),
    ]
