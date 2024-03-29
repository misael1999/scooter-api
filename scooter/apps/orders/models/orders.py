""" Order models """
from django.contrib.gis.db import models
# utilities
from scooter.apps.orders.managers import OrderManager
from scooter.utils.models.scooter import ScooterModel


class Order(ScooterModel):
    user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING)
    customer = models.ForeignKey('customers.Customer', on_delete=models.DO_NOTHING)
    member_station = models.ForeignKey('stations.MemberStation',
                                       on_delete=models.DO_NOTHING,
                                       help_text="For update statistics member station",
                                       related_name="member_station",
                                       blank=True,
                                       null=True)
    delivery_man = models.ForeignKey('delivery_men.DeliveryMan',
                                     on_delete=models.DO_NOTHING, related_name="delivery_man",
                                     null=True, blank=True)
    station = models.ForeignKey('stations.Station', on_delete=models.DO_NOTHING, null=True, blank=True)
    service = models.ForeignKey('common.Service', on_delete=models.DO_NOTHING, null=True, blank=True)
    station_service = models.ForeignKey('stations.StationService', on_delete=models.DO_NOTHING,
                                        related_name="station_service", null=True, blank=True)
    from_address = models.ForeignKey('customers.CustomerAddress', on_delete=models.DO_NOTHING,
                                     help_text='Place of purchase or place of delivery depending on the service',
                                     related_name='from_address', null=True, blank=True)
    to_address = models.ForeignKey('customers.CustomerAddress', on_delete=models.DO_NOTHING,
                                   related_name='to_address', null=True, blank=True)
    # Merchants
    merchant = models.ForeignKey('merchants.Merchant',
                                 on_delete=models.DO_NOTHING, null=True, blank=True)
    merchant_location = models.PointField(geography=True, null=True, blank=True)
    order_price = models.FloatField(null=True, blank=True)
    total_order = models.FloatField(null=True, blank=True)
    increment_price_operating = models.FloatField(default=0)
    has_rate_operating = models.BooleanField(default=False)
    is_delivery_by_store = models.BooleanField(default=False)
    is_order_to_merchant = models.BooleanField(default=False)
    promotion = models.ForeignKey('customers.CustomerPromotion', blank=True, null=True, on_delete=models.DO_NOTHING)

    service_price = models.FloatField()
    indications = models.TextField(blank=True, null=True)
    approximate_price_order = models.CharField(max_length=30, null=True, blank=True)
    date_delivered_order = models.DateTimeField(null=True, blank=True)
    date_update_order = models.DateTimeField(null=True, blank=True)
    order_date = models.DateTimeField()
    order_ready_date = models.DateTimeField(null=True,
                                            blank=True,
                                            help_text="When the order is ready")
    qr_code = models.CharField(max_length=15, blank=True, null=True)
    order_status = models.ForeignKey('common.OrderStatus', on_delete=models.DO_NOTHING, default=1)
    # For notice to user that not response his request
    reason_rejection = models.CharField(max_length=100, blank=True, null=True)
    maximum_response_time = models.DateTimeField()
    phone_number = models.CharField(max_length=15)
    distance = models.FloatField(null=True, blank=True)
    in_process = models.BooleanField(default=False)
    validate_qr = models.BooleanField(default=False)
    is_safe_order = models.BooleanField(default=False)
    # payments
    is_payment_online = models.BooleanField(default=False)
    payment_method = models.PositiveIntegerField(default=1)
    card = models.ForeignKey('payments.Card', on_delete=models.DO_NOTHING,
                             null=True, blank=True)
    order_conekta_id = models.CharField(max_length=80, null=True, blank=True)

    objects = OrderManager()

    def __str__(self):
        return self.qr_code


class OrderDetail(ScooterModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="details")
    product_name = models.CharField(max_length=200)
    picture = models.ImageField(upload_to='orders/pictures/', blank=True, null=True)
    # merchants
    product = models.ForeignKey('merchants.Product', on_delete=models.DO_NOTHING, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    product_price = models.FloatField(null=True, blank=True)
    have_menu_options = models.BooleanField(default=False)

    class Meta:
        db_table = 'orders_order_detail'

    def get_total_detail(self):
        if self.quantity and self.product_price:
            return self.quantity * self.product_price
        return 0


class OrderDetailMenu(ScooterModel):
    detail = models.ForeignKey(OrderDetail, on_delete=models.DO_NOTHING,
                               related_name="menu_options")
    menu = models.ForeignKey('merchants.ProductMenuCategory', on_delete=models.DO_NOTHING,
                             related_name="order_menu_category")
    price = models.FloatField(default=0)
    menu_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'orders_order_detail_menu'


class OrderDetailMenuOption(ScooterModel):
    detail_menu = models.ForeignKey(OrderDetailMenu,
                                    on_delete=models.DO_NOTHING,
                                    related_name="options")
    option = models.ForeignKey('merchants.ProductMenuOption', on_delete=models.DO_NOTHING,
                               related_name="order_menu_option")
    option_name = models.CharField(max_length=100)
    price_option = models.FloatField(blank=True, null=True, default=0)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'orders_order_detail_menu_option'


class HistoryRejectedOrders(ScooterModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_man = models.ForeignKey('delivery_men.DeliveryMan', on_delete=models.CASCADE)
    reason_rejection = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'orders_history_rejected_orders'
