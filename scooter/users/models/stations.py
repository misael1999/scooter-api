# django
from django.db import models
# Utilities
from scooter.utils.models import ScooterModel


class Station(ScooterModel):
    user = models.OneToOneField('users.User', on_delete=models.DO_NOTHING)
    contact_person = models.CharField(max_length=80)
    picture = models.ImageField(upload_to='stations/pictures/', blank=True, null=True)
    station_name = models.CharField(max_length=100)
    station_verified = models.BooleanField(default=False)
    document_verified = models.FileField(upload_to='stations/documents/')

    # Config
    assign_delivery_manually = models.BooleanField(default=False)
    cancellation_policies = models.TextField(blank=True, null=True)

    # stats
    reputation = models.FloatField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_clients = models.PositiveIntegerField(default=0)
    total_delivery_man = models.PositiveIntegerField(default=0)
    total_messages_support = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.station_name
