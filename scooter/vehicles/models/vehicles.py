# django
from django.db import models
# Utilities
from scooter.utils.models import ScooterModel
from django.core.validators import RegexValidator


class Vehicle(ScooterModel):

    station = models.ForeignKey('users.Station', on_delete=models.CASCADE)
    alias = models.CharField(max_length=30)
    model = models.CharField(max_length=50, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)
    plate = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.alias
