# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0014_campparams'),
    ]

    operations = [
        migrations.AddField(
            model_name='campparams',
            name='order_of_distr',
            field=models.IntegerField(null=True, choices=[('1', 'Wall-Ava'), ('2', 'Wall-Ava-Privat'), ('3', 'Ava-Wall'), ('4', 'Ava-Wall-Privat')]),
        ),
    ]
