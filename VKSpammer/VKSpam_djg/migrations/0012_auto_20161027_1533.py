# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0011_auto_20161027_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='campparams',
            name='ava_attach_woman',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=35, blank=True), size=6, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='campparams',
            name='is_considered_user_sex',
            field=models.BooleanField(default='xaxax'),
            preserve_default=False,
        ),
    ]
