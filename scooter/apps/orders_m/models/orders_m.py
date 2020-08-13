""" Order models """
from django.contrib.gis.db import models
# utilities
from scooter.utils.models.scooter import ScooterModel


class OrderMerchant(ScooterModel):
    user = models.ForeignKey('users.User',
                             on_delete=models.DO_NOTHING)
    customer = models.ForeignKey('customers.Customer',
                                 on_delete=models.DO_NOTHING)
    merchant = models.ForeignKey('merchants.Merchant',
                                 on_delete=models.DO_NOTHING)
    member_station = models.ForeignKey('stations.MemberStation',
                                       on_delete=models.DO_NOTHING,
                                       help_text="For update statistics member station",
                                       related_name="member_station",
                                       blank=True,
                                       null=True)
    member_merchant = models.ForeignKey('merchants.MemberMerchant',
                                        on_delete=models.DO_NOTHING,
                                        help_text="For update statistics member merchant",
                                        related_name="member_merchant",
                                        blank=True,
                                        null=True)
    delivery_man = models.ForeignKey('delivery_men.DeliveryMan',
                                     on_delete=models.DO_NOTHING,
                                     related_name="delivery_man",
                                     null=True, blank=True)
    station = models.ForeignKey('stations.Station',
                                on_delete=models.DO_NOTHING,
                                null=True,
                                blank=True)
    service = models.ForeignKey('common.Service',
                                on_delete=models.DO_NOTHING)
    station_service = models.ForeignKey('stations.StationService',
                                        on_delete=models.DO_NOTHING,
                                        related_name="station_service",
                                        null=True, blank=True)
    merchant_location = models.PointField(geography=True)
    to_address = models.ForeignKey('customers.CustomerAddress',
                                   on_delete=models.DO_NOTHING,
                                   related_name='to_address',
                                   null=True,
                                   blank=True)
    service_price = models.FloatField()
    order_price = models.FloatField()
    total_order = models.FloatField()
    indications = models.TextField(blank=True, null=True)
    price_order = models.FloatField()
    maximum_response_time = models.DateTimeField()
    distance = models.FloatField()
    # Dates
    date_delivered_order = models.DateTimeField(null=True, blank=True)
    order_date = models.DateTimeField()
    # helps
    is_delivery_by_store = models.BooleanField()
    qr_code = models.CharField(max_length=15, blank=True, null=True)
    order_status = models.ForeignKey('common.OrderStatus', on_delete=models.DO_NOTHING, default=1)
    phone_number = models.CharField(max_length=15)
    in_process = models.BooleanField(default=False)
    is_safe_order = models.BooleanField(default=False)
    # For notice to user that not response his request
    reason_rejection = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.qr_code


class OrderMerchantDetail(ScooterModel):
    order = models.ForeignKey(OrderMerchant, on_delete=models.CASCADE, related_name="details")
    product = models.ForeignKey('merchants.Product', on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField()
    price_product = models.FloatField()

    class Meta:
        db_table = 'orders_order_merchant_detail'


# class HistoryRejectedOrders(ScooterModel):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     delivery_man = models.ForeignKey('delivery_men.DeliveryMan', on_delete=models.CASCADE)
#     reason_rejection = models.CharField(max_length=100, null=True, blank=True)
#
#     class Meta:
#         db_table = 'orders_history_rejected_orders'
