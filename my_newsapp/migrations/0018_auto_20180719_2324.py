# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-19 23:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_newsapp', '0017_auto_20180710_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='description',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
