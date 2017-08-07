# from third-party applications
from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, DateTimeField, CharField, PositiveIntegerField, BooleanField
from django.urls import reverse_lazy

# from main application
from opd_application.constants import LABORATORY_PROFILE_PAGE_NAME
from opd_application.models.medical_record_models import MedicalRecord


class LaboratoryTest(Model):
    description = CharField(max_length=50)
    order = PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Laboratory Test'
        verbose_name_plural = 'Laboratory Tests'

    def __str__(self):
        return "%s" % self.description


class LaboratoryMeasurementUnit(Model):
    description = CharField(max_length=50)
    is_displayable = BooleanField(default=True)
    is_validatable = BooleanField(default=True)

    class Meta:
        verbose_name = 'Laboratory Measurement Unit'
        verbose_name_plural = 'Laboratory Measurement Units'

    def __str__(self):
        return "%s" % self.description


class LaboratoryTestDetail(Model):
    laboratory_test = ForeignKey(LaboratoryTest)
    laboratory_measurement_unit = ForeignKey(LaboratoryMeasurementUnit)
    description = CharField(max_length=50)
    order = PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Laboratory Test Detail'
        verbose_name_plural = 'Laboratory Test Details'

    def __str__(self):
        return "%s: %s (%s)" % (self.laboratory_test, self.description, self.laboratory_measurement_unit)


class LaboratoryTestDetailChoice(Model):
    laboratory_test_detail = ForeignKey(LaboratoryTestDetail)
    description = CharField(max_length=50)

    class Meta:
        verbose_name = 'Laboratory Test Detail Choice'
        verbose_name_plural = 'Laboratory Test Detail Choices'

    def __str__(self):
        return "%s - %s" % (self.laboratory_test_detail, self.description)


class Laboratory(Model):
    medical_record = ForeignKey(MedicalRecord)

    recorded_by = ForeignKey(User)
    recorded_date = DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse_lazy(LABORATORY_PROFILE_PAGE_NAME, kwargs={'id': str(self.id)})


class LaboratoryResult(Model):
    laboratory = ForeignKey(Laboratory)
    laboratory_test_detail = ForeignKey(LaboratoryTestDetail)
    value = CharField(max_length=100, blank=True)

    is_deleted = BooleanField(default=False)
    updated_by = ForeignKey(User, blank=True)
    updated_date = DateTimeField(blank=True)
