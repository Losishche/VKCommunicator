# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0004_testtable'),
    ]

    operations = [
        migrations.AddField(
            model_name='testtable',
            name='some_field2',
            field=models.CharField(max_length=80, null=True),
            preserve_default=True,
        ),
    ]
