from django.contrib.gis.db import models

# Create your models here.
from scooter.utils.models import ScooterModel


class PaymentMethod(ScooterModel):

    name = models.CharField(max_length=80)
    icon = models.CharField(max_length=30, null=True, blank=True)
    slug_name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'payments_payment_method'

