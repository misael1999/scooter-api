""" Order models """
from django.contrib.gis.db import models
# utilities
from scooter.utils.models.scooter import ScooterModel


class Order(ScooterModel):
    customer = models.ForeignKey('customers.Customer', on_delete=models.DO_NOTHING)
    delivery_man = models.ForeignKey('delivery_men.DeliveryMan',
                                     on_delete=models.DO_NOTHING, related_name="delivery_man",
                                     null=True, blank=True)
    station = models.ForeignKey('stations.Station', on_delete=models.DO_NOTHING)
    station_service = models.ForeignKey('stations.StationService', on_delete=models.DO_NOTHING,
                                        related_name="station_service")
    from_address = models.ForeignKey('customers.CustomerAddress', on_delete=models.DO_NOTHING,
                                     help_text='Place of purchase or place of delivery depending on the service',
                                     related_name='from_address', null=True, blank=True)
    to_address = models.ForeignKey('customers.CustomerAddress', on_delete=models.DO_NOTHING,
                                   related_name='to_address', null=True, blank=True)
    service_price = models.FloatField()
    indications = models.TextField(blank=True, null=True)
    approximate_price_order = models.CharField(max_length=30)
    date_delivered_order = models.DateTimeField(null=True, blank=True)
    qr_code = models.CharField(max_length=15, blank=True, null=True)
    order_status = models.ForeignKey('common.OrderStatus', on_delete=models.DO_NOTHING, default=1)
    # For notice to user that not response his request
    maximum_response_time = models.DateTimeField()
    phone_number = models.CharField(max_length=15)


class OrderDetail(ScooterModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="details")
    product_name = models.CharField(max_length=200)
    picture = models.ImageField(upload_to='orders/pictures/', blank=True, null=True)

    class Meta:
        db_table = 'orders_order_detail'


class HistoryRejectedOrders(ScooterModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_man = models.ForeignKey('delivery_men.DeliveryMan', on_delete=models.CASCADE)
    reason_rejection = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'orders_history_rejected_orders'
