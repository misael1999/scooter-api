""" Categories models """
# django
from django.contrib.gis.db import models
# Utilities
from django.core.validators import FileExtensionValidator

from scooter.utils.models import ScooterModel


class CategoryProducts(ScooterModel):
    name = models.CharField(max_length=70)
    picture = models.ImageField(upload_to='merchants/categories/', blank=True, null=True,
                                validators=[FileExtensionValidator(['jpg', 'png', 'jpeg'])])
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.DO_NOTHING)
    ordering = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name


class SubcategoryProducts(ScooterModel):
    name = models.CharField(max_length=70)
    picture = models.ImageField(upload_to='merchants/subcategories/', blank=True, null=True,
                                validators=[FileExtensionValidator(['jpg', 'png', 'jpeg'])])
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.DO_NOTHING)
    category = models.ForeignKey(CategoryProducts, on_delete=models.DO_NOTHING, related_name="subcategories")
