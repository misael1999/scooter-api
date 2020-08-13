""" Categories models """
# django
from django.contrib.gis.db import models
# Utilities
from scooter.utils.models import ScooterModel


class CategoryProducts(ScooterModel):
    name = models.CharField(max_length=70)
    picture = models.ImageField(upload_to='merchants/categories/', blank=True, null=True)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name
