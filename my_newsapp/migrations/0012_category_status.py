# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-14 15:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_newsapp', '0011_auto_20180614_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='status',
            field=models.CharField(blank=True, choices=[('P', 'Primary'), ('S', 'Secondary')], max_length=1, null=True, unique=True),
        ),
    ]
