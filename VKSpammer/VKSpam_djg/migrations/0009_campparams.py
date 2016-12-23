# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('VKSpam_djg', '0008_remove_vkgroupuserunion_can_post_wall_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='CampParams',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ava_text', models.CharField(max_length=80, blank=True)),
                ('private_text', models.CharField(max_length=120, blank=True)),
                ('wall_text', models.CharField(max_length=120, blank=True)),
                ('ava_attach', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=35, blank=True), size=6)),
                ('private_attach', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=35, blank=True), size=6)),
                ('wall_attach', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=35, blank=True), size=6)),
                ('send_to_ava', models.BooleanField()),
                ('send_to_private', models.BooleanField()),
                ('send_to_wall', models.BooleanField()),
                ('is_daily', models.BooleanField()),
                ('daily_start_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'camp_params',
            },
        ),
    ]
