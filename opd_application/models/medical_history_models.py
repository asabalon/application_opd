# from third-party applications
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse_lazy

# from main application
from opd_application.constants import MEDICAL_HISTORY_PROFILE_PAGE_NAME
from opd_application.models.patient_models import Patient


class MedicalHistoryCategory(models.Model):
    description = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Medical History Category'
        verbose_name_plural = 'Medical History Categories'

    def __str__(self):
        return "%s" % (self.description)


class MedicalHistoryCategoryUnit(models.Model):
    description = models.CharField(max_length=50)
    is_displayable = models.BooleanField(default=True)
    is_validatable = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Medical History Category Unit'
        verbose_name_plural = 'Medical History Category Units'

    def __str__(self):
        return "%s" % self.description


class MedicalHistoryCategoryDetail(models.Model):
    medical_history_category = models.ForeignKey(MedicalHistoryCategory)
    medical_history_category_unit = models.ForeignKey(MedicalHistoryCategoryUnit)
    description = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Medical History Category Detail'
        verbose_name_plural = 'Medical History Category Details'

    def __str__(self):
        return "%s: %s (%s)" % (self.medical_history_category, self.description, self.medical_history_category_unit)


class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient)

    recorded_by = models.ForeignKey(User, related_name='created_by')
    recorded_date = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse_lazy(MEDICAL_HISTORY_PROFILE_PAGE_NAME, kwargs={'id': str(self.id)})


class MedicalHistoryDetail(models.Model):
    medical_history = models.ForeignKey(MedicalHistory)
    medical_history_category_detail = models.ForeignKey(MedicalHistoryCategoryDetail)
    value = models.CharField(max_length=100, blank=True)
