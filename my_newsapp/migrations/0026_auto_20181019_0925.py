# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-19 09:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_newsapp', '0025_remove_file_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
