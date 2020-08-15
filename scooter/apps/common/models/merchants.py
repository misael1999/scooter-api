""" Merchants common models """
# Django
from django.db import models
# Utilities
from scooter.utils.models.scooter import ScooterModel


class CategoryMerchant(ScooterModel):

    name = models.CharField(max_length=70)
    slug_name = models.CharField(max_length=50)
    image = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class SubcategoryMerchant(ScooterModel):
    name = models.CharField(max_length=70)
    slug_name = models.CharField(max_length=50)
    category = models.ForeignKey(CategoryMerchant, on_delete=models.CASCADE, related_name="subcategories")
    image = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name
