# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-11 15:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_newsapp', '0018_auto_20180719_2324'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='my_newsapp.Article')),
            ],
        ),
    ]
