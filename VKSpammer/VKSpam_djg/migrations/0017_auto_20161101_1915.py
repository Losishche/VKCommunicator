# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0016_auto_20161028_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='botssenders',
            name='vk_token',
            field=models.CharField(blank=True, null=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='botssenders',
            name='vk_token_expired',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
