from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, DateTimeField, CharField, PositiveIntegerField, BooleanField
from django.urls import reverse_lazy

from opd_application.constants import PRESCRIPTION_PROFILE_PAGE_NAME
from opd_application.models.medical_record_models import MedicalRecord
from opd_application.models.models import Dosage, Package, Frequency, DesignatedTime


class Medicine(Model):
    description = CharField(max_length=50)
    order = PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Medicine'
        verbose_name_plural = 'Medicines'

    def __str__(self):
        return "%s" % self.description


class Prescription(Model):
    medical_record = ForeignKey(MedicalRecord)

    recorded_by = ForeignKey(User)
    recorded_date = DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse_lazy(PRESCRIPTION_PROFILE_PAGE_NAME, kwargs={'id': str(self.id)})


class PrescriptionEntry(Model):
    prescription = ForeignKey(Prescription)
    medicine = ForeignKey(Medicine, blank=True)
    dosage = ForeignKey(Dosage, blank=True)
    package = ForeignKey(Package, blank=True)
    frequency = ForeignKey(Frequency, blank=True)
    designated_time = ForeignKey(DesignatedTime, blank=True)

    is_deleted = BooleanField(default=False)
    updated_by = ForeignKey(User, blank=True)
    updated_date = DateTimeField(blank=True)

    def __str__(self):
        return "%s - %s - %s - %s - %s - %s" % (
            self.prescription, self.medicine, self.dosage, self.package, self.frequency, self.designated_time)
