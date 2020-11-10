# django
from django.contrib.gis.db import models
# Utilities
from scooter.utils.models import ScooterModel


class StationZone(ScooterModel):

    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=150, blank=True, null=True)
    poly = models.GeometryField(blank=True, null=True)

    def __str__(self):
        return self.name
