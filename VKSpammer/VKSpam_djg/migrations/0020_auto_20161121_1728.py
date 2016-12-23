# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0019_privatmessages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privatmessages',
            name='message',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
