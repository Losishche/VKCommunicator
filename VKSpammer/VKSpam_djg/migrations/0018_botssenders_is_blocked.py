# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0017_auto_20161101_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='botssenders',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]
