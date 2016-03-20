from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class User(User):
    birth_date = models.DateField()

    middle_name = models.CharField(max_length=30, blank=True)

    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return "%s, %s %s" % (self.last_name, self.first_name, self.middle_name)
