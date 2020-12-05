from django.contrib.gis.db import models

# Create your models here.
from scooter.utils.models import ScooterModel


class CustomerConekta(ScooterModel):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, blank=True, null=True)
    customer = models.OneToOneField('customers.Customer', on_delete=models.CASCADE, blank=True, null=True)
    customer_conekta_id = models.CharField(max_length=100)

    def __str__(self):
        return self.customer.name

    class Meta:
        db_table = 'payments_customer_conekta'


class Card(ScooterModel):
    customer_conekta = models.ForeignKey(CustomerConekta, on_delete=models.DO_NOTHING,
                                         blank=True, null=True)
    customer = models.OneToOneField('customers.Customer', on_delete=models.CASCADE,
                                    related_name='cards', blank=True, null=True)
    source_id = models.CharField(max_length=100, null=True, blank=True)
    card_token = models.CharField(max_length=100)
    last_four = models.CharField(max_length=4)
    default = models.BooleanField(default=False)
    brand = models.CharField(max_length=20, default='Visa')

    def __str__(self):
        return self.last_four

    class Meta:
        db_table = "customers_customer_card"
