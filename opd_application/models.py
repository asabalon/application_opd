from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django_countries.fields import CountryField


# TODO: Move models into separate files
# TODO: Add str function to every model for Logging

# Create your models here.
class Complaint(models.Model):
    description = models.CharField(max_length=50)

    def __str__(self):
        return "%s" % (self.description)


class LungChoice(models.Model):
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Lung Choice'
        verbose_name_plural = 'Lung Choices'

    def __str__(self):
        return "%s" % (self.description)


class RateChoice(models.Model):
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Rate Choice'
        verbose_name_plural = 'Rate Choices'

    def __str__(self):
        return "%s" % (self.description)


class RhythmChoice(models.Model):
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Rhythm Choice'
        verbose_name_plural = 'Rhythm Choices'

    def __str__(self):
        return "%s" % (self.description)


class AbdomenChoice(models.Model):
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Abdomen Choice'
        verbose_name_plural = 'Abdomen Choices'

    def __str__(self):
        return "%s" % (self.description)


class ExtremitiesChoice(models.Model):
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Extremities Choice'
        verbose_name_plural = 'Extremities Choices'

    def __str__(self):
        return "%s" % (self.description)


class EENTChoice(models.Model):
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'EENT Choice'
        verbose_name_plural = 'EENT Choices'

    def __str__(self):
        return "%s" % (self.description)


class Patient(models.Model):
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Undefined'),
    )

    MARITAL_CHOICES = (
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
        ('R', 'Widower'),
    )

    photo = models.ImageField(upload_to='img', blank=True)

    first_name = models.CharField(max_length=25)
    middle_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=25)
    birth_date = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    marital_status = models.CharField(max_length=1, choices=MARITAL_CHOICES)

    address_street = models.CharField(max_length=50)
    address_district = models.CharField(max_length=50)
    address_city = models.CharField(max_length=50)
    address_province = models.CharField(max_length=50)
    address_postal = models.CharField(max_length=50)
    address_country = CountryField(default='PH')
    contact_number = models.CharField(max_length=10)
    referred_by = models.CharField(max_length=50, blank=True)

    created_by = models.ForeignKey(User, related_name='p_recorded_by')
    creation_date = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now=False, null=True)
    last_updated_by = models.ForeignKey(User, related_name='p_updated_by', null=True)

    class Meta:
        unique_together = (('first_name', 'last_name', 'birth_date'),)

    def __str__(self):
        return "%s, %s %s" % (self.last_name, self.first_name, self.middle_name)

    def get_absolute_url(self):
        return reverse_lazy('opd:profile', kwargs={'id': str(self.id)})


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


class PhysicalExam(models.Model):
    medical_record = models.ForeignKey(MedicalRecord)

    recorded_by = models.ForeignKey(User)
    recorded_date = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse_lazy('opd:exam', kwargs={'id': str(self.id)})


class PhysicalExamKey(models.Model):
    key_value = models.CharField(max_length=25)
    display_value = models.CharField(max_length=25)

    class Meta:
        verbose_name = 'Physical Exam Key'
        verbose_name_plural = 'Physical Exam Keys'

    def __str__(self):
        return "%s" % (self.display_value)


class PhysicalExamDetail(models.Model):
    physical_exam = models.ForeignKey(PhysicalExam)
    key = models.ForeignKey(PhysicalExamKey)
    real_value = models.CharField(max_length=100)
    str_value = models.CharField(max_length=100)


class Laboratory(models.Model):
    medical_record = models.ForeignKey(MedicalRecord)

    recorded_by = models.ForeignKey(User)
    recorded_date = models.DateTimeField(auto_now=True)


class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord)

    recorded_by = models.ForeignKey(User)
    recorded_date = models.DateTimeField(auto_now=True)


class Diagnosis(models.Model):
    medical_record = models.ForeignKey(MedicalRecord)

    recorded_by = models.ForeignKey(User)
    recorded_date = models.DateTimeField(auto_now=True)


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

    class Meta:
        verbose_name = 'Medical History Category Unit'
        verbose_name_plural = 'Medical History Category Units'

    def __str__(self):
        return "%s" % (self.description)


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


class MedicalHistoryCategoryDetailKey(models.Model):
    key_value = models.CharField(max_length=25)
    medical_history_category_detail = models.ForeignKey(MedicalHistoryCategoryDetail)

    class Meta:
        verbose_name = 'Medical History Category Detail Key'
        verbose_name_plural = 'Medical History Category Detail Keys'

    def __str__(self):
        return "%s: %s" % (self.medical_history_category_detail, self.key_value)


class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient)

    recorded_by = models.ForeignKey(User, related_name='created_by')
    recorded_date = models.DateTimeField(auto_now=True)


class MedicalHistoryDetail(models.Model):
    medical_history = models.ForeignKey(MedicalHistory)
    medical_history_category_detail = models.ForeignKey(MedicalHistoryCategoryDetail)
    value = models.CharField(max_length=100)


class MaintenanceMedication(models.Model):
    patient = models.ForeignKey(Patient)

    recorded_by = models.ForeignKey(User)
    recorded_date = models.DateTimeField(auto_now=True)
