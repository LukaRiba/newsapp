# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-05 12:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_newsapp', '0013_auto_20180703_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='Galery',
            fields=[
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='my_newsapp.Article')),
                ('thumbnail_image', models.ImageField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('description', models.CharField(max_length=300)),
                ('galery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='my_newsapp.Galery')),
            ],
        ),
        migrations.RemoveField(
            model_name='article',
            name='first_image',
        ),
        migrations.RemoveField(
            model_name='article',
            name='first_part',
        ),
        migrations.RemoveField(
            model_name='article',
            name='second_image',
        ),
        migrations.RemoveField(
            model_name='article',
            name='second_part',
        ),
        migrations.RemoveField(
            model_name='article',
            name='thumbnail_image',
        ),
        migrations.AddField(
            model_name='article',
            name='text',
            field=models.TextField(default='null'),
            preserve_default=False,
        ),
    ]
