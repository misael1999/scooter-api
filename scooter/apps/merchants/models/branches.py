""" Merchants models """
# django
from django.contrib.gis.db import models
# Utilities

from scooter.utils.models import ScooterModel


class Branch(ScooterModel):
    name = models.CharField(max_length=150)
    user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.DO_NOTHING)
    location = models.PointField(srid=4326)
    has_stock = models.BooleanField(default=False)


class BranchProduct(ScooterModel):
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING)
    product = models.ForeignKey('merchants.Product', on_delete=models.DO_NOTHING)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.DO_NOTHING)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
