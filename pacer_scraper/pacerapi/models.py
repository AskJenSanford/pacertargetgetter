from django.db import models


# Create your models here.

class Address(models.Model):
    case_number = models.CharField("Case Number", max_length=255)
    address = models.CharField("Address", max_length=255)

    def __str__(self):
        return self.case_number
