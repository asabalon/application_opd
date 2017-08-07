# from third-party applications
from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, DateTimeField, CharField, PositiveIntegerField, BooleanField
from django.urls import reverse_lazy

# from main application
from opd_application.constants import MEDICATION_PROFILE_PAGE_NAME
from opd_application.models.patient_models import Patient
from opd_application.models.models import Dosage, Package, Frequency, DesignatedTime


class Medication(Model):
    patient = ForeignKey(Patient)

    recorded_by = ForeignKey(User, related_name='created_by')
    recorded_date = DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse_lazy(MEDICATION_PROFILE_PAGE_NAME, kwargs={'id': str(self.id)})


class MedicationEntry(Model):
    medication = ForeignKey(Medication)
    dosage = ForeignKey(Dosage)
    package = ForeignKey(Package)
    frequency = ForeignKey(Frequency)
    designated_time = ForeignKey(DesignatedTime)
    description = CharField(max_length=50)
