# django
from django.contrib.gis.db import models
# Utilities
from scooter.utils.models import ScooterModel


class StationZone(ScooterModel):

    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=150, blank=True, null=True)
    poly = models.GeometryField(blank=True, null=True)
    type = models.ForeignKey('common.TypeZone', on_delete=models.DO_NOTHING)
    # When is to promotion
    base_rate_price = models.FloatField(blank=True, null=True)
    from_hour = models.TimeField(blank=True, null=True)
    to_hour = models.TimeField(blank=True, null=True)
    # Helps
    has_price = models.BooleanField(default=False)
    has_schedule = models.BooleanField(default=False)

    def __str__(self):
        return self.name
