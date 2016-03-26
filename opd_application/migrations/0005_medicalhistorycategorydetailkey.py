# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-24 20:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('opd_application', '0004_auto_20160323_1024'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicalHistoryCategoryDetailKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_value', models.CharField(max_length=25)),
                ('medical_history_category_detail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd_application.MedicalHistoryCategoryDetail')),
            ],
            options={
                'verbose_name': 'Medical History Category Detail Key',
                'verbose_name_plural': 'Medical History Category Detail Keys',
            },
        ),
    ]
