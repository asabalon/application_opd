# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-22 21:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opd_application', '0002_medicalrecord_additional_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaintenanceMedication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_date', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd_application.Patient')),
                ('recorded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MedicalHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_date', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd_application.Patient')),
                ('recorded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MedicalHistoryCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Medical History Category',
                'verbose_name_plural': 'Medical History Categories',
            },
        ),
        migrations.CreateModel(
            name='MedicalHistoryCategoryDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
                ('medical_history_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd_application.MedicalHistoryCategory')),
            ],
            options={
                'verbose_name': 'Medical History Category Detail',
                'verbose_name_plural': 'Medical History Category Details',
            },
        ),
        migrations.CreateModel(
            name='MedicalHistoryCategoryUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Medical History Category Unit',
                'verbose_name_plural': 'Medical History Category Units',
            },
        ),
        migrations.CreateModel(
            name='MedicalHistoryDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('medical_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd_application.MedicalHistory')),
                ('medical_history_category_detail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd_application.MedicalHistoryCategoryDetail')),
            ],
        ),
        migrations.AddField(
            model_name='medicalhistorycategorydetail',
            name='medical_history_category_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='opd_application.MedicalHistoryCategoryUnit'),
        ),
    ]
