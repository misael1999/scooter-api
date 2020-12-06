""" Merchants models """
# django
from django.contrib.gis.db import models
# Utilities

from scooter.utils.models import ScooterModel


class MerchantPaymentMethod(ScooterModel):
    merchant = models.ForeignKey('merchants.Merchant',  on_delete=models.DO_NOTHING, related_name="payment_methods")
    payment_method = models.ForeignKey('payments.PaymentMethod', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "merchants_merchant_payment_method"
