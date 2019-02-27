# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-27 21:53
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_newsapp', '0030_auto_20190227_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='short_description_en',
            field=models.TextField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='slug_en',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='title'),
        ),
        migrations.AddField(
            model_name='article',
            name='text_en',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='title_en',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
