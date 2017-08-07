from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model, CharField, PositiveIntegerField

from opd_application.models.patient_models import Patient


class MaintenanceMedication(models.Model):
    patient = models.ForeignKey(Patient)

    recorded_by = models.ForeignKey(User)
    recorded_date = models.DateTimeField(auto_now=True)


class Dosage(Model):
    description = CharField(max_length=50)
    order = PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Dosage'
        verbose_name_plural = 'Dosages'

    def __str__(self):
        return "%s" % self.description


class Package(Model):
    description = CharField(max_length=50)
    order = PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Package'
        verbose_name_plural = 'Package'

    def __str__(self):
        return "%s" % self.description


class Frequency(Model):
    description = CharField(max_length=50)
    order = PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Frequency'
        verbose_name_plural = 'Frequencies'

    def __str__(self):
        return "%s" % self.description


class DesignatedTime(Model):
    description = CharField(max_length=50)
    order = PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Designated Time'
        verbose_name_plural = 'Designated Times'

    def __str__(self):
        return "%s" % self.description