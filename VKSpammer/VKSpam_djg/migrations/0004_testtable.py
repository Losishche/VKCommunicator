# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0003_delete_exp'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestTable',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('some_field', models.CharField(max_length=80, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
