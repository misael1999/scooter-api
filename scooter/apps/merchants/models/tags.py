""" Products models """
# django
from django.contrib.gis.db import models
# Utilities
from django.core.validators import FileExtensionValidator

from scooter.utils.models import ScooterModel


class Tag(ScooterModel):
    name = models.CharField(max_length=50)
    picture = models.ImageField(upload_to='merchants/tags/', blank=True, null=True,
                                validators=[FileExtensionValidator(['jpg', 'png', 'jpeg'])])
    area = models.ForeignKey('common.Area', on_delete=models.DO_NOTHING, default=1)


class MerchantTag(ScooterModel):
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.DO_NOTHING, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.DO_NOTHING, related_name="merchants_tags")
    tag_name = models.CharField(max_length=50)

