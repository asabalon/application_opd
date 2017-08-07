from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse_lazy

from opd_application.models.medical_record_models import MedicalRecord


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
