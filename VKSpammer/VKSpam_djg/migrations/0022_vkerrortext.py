# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0021_auto_20161123_1737'),
    ]

    operations = [
        migrations.CreateModel(
            name='VkErrorText',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('vk_error_code', models.IntegerField(null=True)),
                ('text', models.CharField(max_length=120)),
            ],
            options={
                'db_table': 'vk_error_text',
                'managed': True,
            },
        ),
    ]
