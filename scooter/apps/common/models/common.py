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


class TypeVehicle(ScooterModel):
    name = models.CharField(max_length=30)
    slug_name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class AppVersion(ScooterModel):
    alias = models.CharField(max_length=30)
    comments = models.CharField(max_length=40)
    version_number = models.CharField(max_length=5)
    build_number = models.PositiveIntegerField(default=1)
    priority = models.BooleanField(default=False)
    app = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.alias

