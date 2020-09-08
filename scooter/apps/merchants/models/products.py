""" Products models """
# django
from django.contrib.gis.db import models
# Utilities
from django.core.validators import FileExtensionValidator

from scooter.utils.models import ScooterModel


class TypeOption(ScooterModel):
    name = models.CharField(max_length=50)
    slug_name = models.CharField(max_length=50)


class Product(ScooterModel):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=400)
    description_long = models.TextField(null=True, blank=True)
    stock = models.PositiveIntegerField(default=100, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    price = models.FloatField()
    category = models.ForeignKey('merchants.CategoryProducts', on_delete=models.DO_NOTHING, related_name="products")
    subcategory = models.ForeignKey('merchants.SubcategoryProducts',
                                    on_delete=models.DO_NOTHING,
                                    related_name="products", null=True, blank=True)
    picture = models.ImageField(upload_to='merchants/products/', blank=True, null=True,
                                validators=[FileExtensionValidator(['jpg', 'png', 'jpeg'])])
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.DO_NOTHING)
    # helps
    have_menu = models.BooleanField(default=False)
    # statistics
    total_sales = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class ProductMenuCategory(ScooterModel):
    name = models.CharField(max_length=150)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name="menu_categories")
    is_obligatory = models.BooleanField()
    limit_options_choose = models.PositiveIntegerField(default=0)
    min_options_choose = models.PositiveIntegerField()
    max_options_choose = models.PositiveIntegerField()
    is_range = models.BooleanField(default=False)
    have_quantity = models.BooleanField(default=False)
    min_quantity = models.PositiveIntegerField(default=0)
    max_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        get_latest_by = 'created'
        ordering = ['created']

    def __str__(self):
        return self.name


class ProductMenuOption(ScooterModel):
    menu = models.ForeignKey(ProductMenuCategory, on_delete=models.DO_NOTHING, related_name="options")
    name = models.CharField(max_length=90)
    price = models.FloatField(null=True, blank=True)

    class Meta:
        get_latest_by = 'created'
        ordering = ['created']

    def __str__(self):
        return self.name

