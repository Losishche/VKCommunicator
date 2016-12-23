# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='exp',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('vk_experiment', models.BigIntegerField(blank=True, null=True)),
            ],
        ),
    ]
