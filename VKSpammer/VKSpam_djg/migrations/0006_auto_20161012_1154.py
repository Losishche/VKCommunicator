# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0005_testtable_some_field2'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vkgroupuserunion',
            options={'managed': True},
        ),
    ]
