# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-01 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_newsapp', '0003_article_short_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='short_description',
            field=models.TextField(max_length=300),
        ),
    ]
