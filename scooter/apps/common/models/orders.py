""" Common order models """
# Django
from django.db import models


class OrderStatus(models.Model):
    name = models.CharField(max_length=60)
    slug_name = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    type_service = models.ForeignKey('common.Service', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'common_order_status'

    def __str__(self):
        return self.name
