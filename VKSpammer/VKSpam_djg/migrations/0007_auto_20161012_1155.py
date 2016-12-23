# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0006_auto_20161012_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='vkgroupuserunion',
            name='can_post_wall_comment',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='vkgroupuserunion',
            name='have_post_wall_comment',
            field=models.NullBooleanField(),
        ),
    ]
