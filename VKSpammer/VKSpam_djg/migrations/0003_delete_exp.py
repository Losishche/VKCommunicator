# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0002_exp'),
    ]

    operations = [
        migrations.DeleteModel(
            name='exp',
        ),
    ]
