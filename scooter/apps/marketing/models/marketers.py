""" Marketers models """
# django
from django.contrib.gis.db import models
# Utilities
from scooter.utils.models import ScooterModel


class Marketer(ScooterModel):
    user = models.OneToOneField('users.User', on_delete=models.DO_NOTHING)
    picture = models.ImageField(upload_to='marketers/pictures/', blank=True, null=True)
    full_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=15)
    # stats

    def __str__(self):
        return self.full_name
