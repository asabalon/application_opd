from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse_lazy
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


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
    contact_number = PhoneNumberField(max_length=15)
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
