# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0007_auto_20161012_1155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vkgroupuserunion',
            name='can_post_wall_comment',
        ),
    ]
