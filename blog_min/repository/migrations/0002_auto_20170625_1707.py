# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-25 09:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='avatar',
            field=models.ImageField(null=True, upload_to='static/imgs/avatar', verbose_name='头像'),
        ),
    ]
