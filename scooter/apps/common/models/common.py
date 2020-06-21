""" Common models """
from django.db import models
# Utilities
from scooter.utils.models.scooter import ScooterModel


class Service(ScooterModel):
    name = models.CharField(max_length=30)
    slug_name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Schedule(ScooterModel):
    name = models.CharField(max_length=30)
    slug_name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        get_latest_by = 'created'
        ordering = ['id']


class TypeAddress(ScooterModel):
    name = models.CharField(max_length=30)
    slug_name = models.CharField(max_length=30)

    def __str__(self):
        return self.name