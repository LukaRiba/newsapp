# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-05 13:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_newsapp', '0014_auto_20180705_1233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='galery',
            name='article',
        ),
        migrations.RemoveField(
            model_name='image',
            name='galery',
        ),
        migrations.AddField(
            model_name='image',
            name='article',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='images', to='my_newsapp.Article'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Galery',
        ),
    ]