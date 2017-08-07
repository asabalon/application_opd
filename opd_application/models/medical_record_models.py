from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse_lazy

from opd_application.models.patient_models import Patient


class Complaint(models.Model):
    description = models.CharField(max_length=50)

    def __str__(self):
        return "%s" % (self.description)


class MedicalRecord(models.Model):
    complaint = models.ManyToManyField(Complaint)
    patient = models.ForeignKey(Patient)
    additional_info = models.CharField(max_length=100, blank=True)

    recorded_by = models.ForeignKey(User, related_name='mr_recorded_by')
    recorded_date = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now=False, null=True)
    last_updated_by = models.ForeignKey(User, related_name='mr_updated_by', null=True)

    def get_absolute_url(self):
        return reverse_lazy('opd:medical', kwargs={'id': str(self.id)})