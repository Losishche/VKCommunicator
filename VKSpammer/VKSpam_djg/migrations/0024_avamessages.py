# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0023_auto_20161201_1624'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvaMessages',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ava_message', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'db_table': 'ava_messages',
                'managed': True,
            },
        ),
    ]
