# from third-party applications
from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, DateTimeField, CharField, PositiveIntegerField, BooleanField
from django.urls import reverse_lazy

# from main application
from opd_application.constants import DIAGNOSIS_PROFILE_PAGE_NAME
from opd_application.models.medical_record_models import MedicalRecord


class DiagnosisCategory(Model):
    description = CharField(max_length=50)
    group = PositiveIntegerField(default=1)
    level = PositiveIntegerField(default=1)
    order = PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Diagnosis Category'
        verbose_name_plural = 'Diagnosis Categories'

    def __str__(self):
        return "%s" % self.description


class DiagnosisCategoryChoice(Model):
    diagnosis_category = ForeignKey(DiagnosisCategory)
    description = CharField(max_length=50)
    order = PositiveIntegerField(default=1)
    is_general_term = BooleanField(default=False)

    class Meta:
        verbose_name = 'Diagnosis Category Choice'
        verbose_name_plural = 'Diagnosis Category Choices'

    def __str__(self):
        return "%s" % self.description


class Diagnosis(Model):
    medical_record = ForeignKey(MedicalRecord)

    recorded_by = ForeignKey(User)
    recorded_date = DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse_lazy(DIAGNOSIS_PROFILE_PAGE_NAME, kwargs={'id': str(self.id)})


class DiagnosisEntry(Model):
    diagnosis = ForeignKey(Diagnosis)
    diagnosis_category = ForeignKey(DiagnosisCategory)
    value = CharField(max_length=50, blank=True)
    remark = CharField(max_length=100, blank=True)

    updated_by = ForeignKey(User, blank=True)
    updated_date = DateTimeField(blank=True)
