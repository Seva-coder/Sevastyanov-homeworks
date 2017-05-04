# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-01 11:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('create', '0003_delete_creation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Roadmap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roadmap_name', models.CharField(max_length=50, verbose_name='Название Roadmap:')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Название задачи:')),
                ('state', models.CharField(max_length=11, verbose_name='статус:')),
                ('estimate', models.DateTimeField(verbose_name='Срок выполнения')),
                ('roadmap', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='create.Roadmap')),
            ],
        ),
    ]
