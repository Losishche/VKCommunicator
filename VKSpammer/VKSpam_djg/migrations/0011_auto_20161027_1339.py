# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0010_auto_20161027_1327'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campparams',
            options={'managed': True},
        ),
    ]
