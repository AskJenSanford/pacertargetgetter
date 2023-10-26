from django.db import models

# Create your models here.
CHOICES = (
    ("PROCESSING", "PROCESSING"),
    ("DONE", "DONE")
)


class Address(models.Model):
    case_number = models.CharField("Case Number", max_length=255, unique=True)
    address = models.JSONField()
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return self.case_number


class Status(models.Model):
    case_number = models.CharField("Case Number", max_length=255)
    status = models.CharField("Status", choices=CHOICES, max_length=255, unique=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return self.case_number
