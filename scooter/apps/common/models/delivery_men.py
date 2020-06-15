""" Delivery men models """
# Django
from django.db import models


class DeliveryManStatus(models.Model):
    name = models.CharField(max_length=60)
    slug_name = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'common_delivery_man_status'

    def __str__(self):
        return self.name
