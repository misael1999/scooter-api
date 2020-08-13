""" Products models """
# django
from django.contrib.gis.db import models
# Utilities
from scooter.utils.models import ScooterModel


class Product(ScooterModel):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=400)
    description_long = models.TextField(null=True, blank=True)
    stock = models.PositiveIntegerField()
    price = models.FloatField()
    category = models.ForeignKey('merchants.CategoryProducts', on_delete=models.DO_NOTHING)
    picture = models.ImageField(upload_to='merchants/products/', blank=True, null=True)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.DO_NOTHING)
    # statistics
    total_sales = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
