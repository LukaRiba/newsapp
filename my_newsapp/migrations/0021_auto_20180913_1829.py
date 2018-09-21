# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-13 18:29
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_newsapp', '0020_auto_20180911_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='files/', validators=[django.core.validators.FileExtensionValidator(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip'])]),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', validators=[django.core.validators.FileExtensionValidator(['bmp', 'gif', 'png', 'jpg', 'jpeg'])]),
        ),
    ]