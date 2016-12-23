# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0022_vkerrortext'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vkerrortext',
            name='vk_error_code',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
