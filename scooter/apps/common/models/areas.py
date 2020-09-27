""" Common models """
from django.contrib.gis.db import models
# Utilities
from scooter.apps.common.models import Status
from scooter.utils.models.scooter import ScooterModel


class Area(ScooterModel):
    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    poly = models.GeometryField(blank=True, null=True, geography=True)


class Zone(ScooterModel):
    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    poly = models.GeometryField(blank=True, null=True, geography=True)
    area = models.ForeignKey(Area, on_delete=models.DO_NOTHING)
