# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-02 12:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0005_auto_20180802_1209'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='parent',
        ),
    ]
