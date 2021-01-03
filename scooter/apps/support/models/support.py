from django.db import models
from scooter.utils.models import ScooterModel


class SupportType(models.Model):
    name = models.CharField(max_length=70)
    slug_name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class SupportStatus(models.Model):
    name = models.CharField(max_length=70)
    slug_name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Support(ScooterModel):

    sku = models.CharField(max_length=15)
    issue = models.CharField(max_length=80)
    is_to_order = models.BooleanField(default=False)
    is_to_help = models.BooleanField(default=False, help_text="Support between customer and station")
    is_to_delivery_man = models.BooleanField(default=False, help_text="Support between customer and delivery man")
    is_open = models.BooleanField(default=True)
    support_type = models.ForeignKey(SupportType, on_delete=models.DO_NOTHING)
    finish_date = models.DateTimeField(null=True, blank=True)
    order_sku = models.CharField(max_length=10, null=True, blank=True)
    order_details = models.TextField(null=True, blank=True)
    order = models.ForeignKey('orders.Order', null=True, blank=True, on_delete=models.DO_NOTHING)
    delivery_man = models.ForeignKey('delivery_men.DeliveryMan', blank=True, null=True, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey('customers.Customer', blank=True, null=True, on_delete=models.DO_NOTHING)
    user = models.ForeignKey('users.User', blank=True, null=True, on_delete=models.DO_NOTHING, help_text="")
    station = models.ForeignKey('stations.Station', on_delete=models.DO_NOTHING)
    support_status = models.ForeignKey(SupportStatus, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.sku


class SupportMessage(ScooterModel):
    text = models.TextField()
    sender_by = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, related_name="sender_by")
    receiver_by = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, related_name="receiver_by")
    viewed = models.BooleanField(default=False)
    viewed_date = models.DateTimeField(null=True, blank=True)
    support = models.ForeignKey(Support, on_delete=models.DO_NOTHING, related_name="messages")

    def __str__(self):
        return self.text
