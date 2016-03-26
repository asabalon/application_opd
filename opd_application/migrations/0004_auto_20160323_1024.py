# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-23 02:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('opd_application', '0003_auto_20160323_0548'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalhistorycategory',
            name='order',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='medicalhistorycategorydetail',
            name='order',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='medicalhistorycategorydetail',
            name='medical_history_category_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd_application.MedicalHistoryCategoryUnit'),
        ),
    ]