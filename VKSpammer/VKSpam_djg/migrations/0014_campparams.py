# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0013_delete_campparams'),
    ]

    operations = [
        migrations.CreateModel(
            name='CampParams',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('is_considered_user_sex', models.BooleanField()),
                ('ava_text', models.CharField(max_length=80, blank=True)),
                ('private_text', models.CharField(max_length=120, blank=True)),
                ('wall_text', models.CharField(max_length=120, blank=True)),
                ('ava_attach', django.contrib.postgres.fields.ArrayField(size=6, base_field=models.CharField(max_length=35, blank=True))),
                ('ava_attach_woman', django.contrib.postgres.fields.ArrayField(size=6, base_field=models.CharField(max_length=35, blank=True))),
                ('private_attach', django.contrib.postgres.fields.ArrayField(size=6, base_field=models.CharField(max_length=35, blank=True))),
                ('wall_attach', django.contrib.postgres.fields.ArrayField(size=6, base_field=models.CharField(max_length=35, blank=True))),
                ('send_to_ava', models.BooleanField()),
                ('send_to_private', models.BooleanField()),
                ('send_to_wall', models.BooleanField()),
                ('is_daily', models.BooleanField()),
                ('daily_start_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'camp_params',
                'managed': True,
            },
        ),
    ]
