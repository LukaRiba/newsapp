# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-03 12:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_newsapp', '0012_category_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.RenameField(
            model_name='article',
            old_name='image1',
            new_name='first_image',
        ),
        migrations.RenameField(
            model_name='article',
            old_name='image2',
            new_name='second_image',
        ),
    ]