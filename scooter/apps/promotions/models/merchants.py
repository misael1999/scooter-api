from django.db import models
from scooter.utils.models import ScooterModel


class MerchantPromotionType(ScooterModel):
    name = models.CharField(max_length=100)
    slug_name = models.CharField(max_length=50)


class MerchantPromotion(ScooterModel):
    """ Promociones por comercio """
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    is_available = models.BooleanField(default=True)
    from_date = models.DateTimeField(null=True, blank=True)
    to_date = models.DateTimeField(null=True, blank=True)
    promotion_type = models.ForeignKey(MerchantPromotionType, on_delete=models.DO_NOTHING)
    station = models.ForeignKey('stations.Station', on_delete=models.DO_NOTHING)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.DO_NOTHING)
    reason_not_available = models.CharField(max_length=150, null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "merchant_promotion"


class MerchantPromotionRule(ScooterModel):
    """ Reglas de promoción """
    merchant_promotion = models.OneToOneField(MerchantPromotion, on_delete=models.DO_NOTHING, related_name="rules")
    # Start booleans flags
    # Si es periodico no debe tener presupuesto
    is_periodic = models.BooleanField()
    has_limit_usage = models.BooleanField()
    # is_discount_per_product = models.BooleanField(help_text="Descuento por producto")
    # is_discount_delivery = models.BooleanField(help_text="Descuento de envío")
    is_discount_percentage = models.BooleanField()
    is_coupon_code = models.BooleanField(default=False)
    # End booleans flags
    # Si la promoción si es compartida
    is_shared_promotion = models.BooleanField(default=False, help_text="Si la promocion en compartida por la central")
    station_payment_percentage = models.FloatField(default=0, help_text="Pago por parte de la central")
    merchant_payment_percentage = models.FloatField(default=100, help_text="Pago por parte del comercio")
    # Aqui Termina si la promoción es compartida
    minimum_order_price = models.FloatField()
    discount_amount = models.FloatField()
    usage_limit = models.PositiveIntegerField(blank=True, null=True)
    budget = models.FloatField(null=True, blank=True, help_text="Presupuesto para la promocion")
    # Statistics fields
    total_usages = models.PositiveIntegerField(default=0)
    approximate_total_usages = models.PositiveIntegerField(default=0)
    amount_spent = models.FloatField(null=True, blank=True, help_text="Gasto hasta el momento")
    coupon_code = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        db_table = "merchant_promotion_rules"

# class MerchantPromotionPrice(ScooterModel):
#


class MerchantPromotionProduct(ScooterModel):
    """ Productos que se aplicara la promoción """
    promotion = models.ForeignKey(MerchantPromotion, on_delete=models.DO_NOTHING, related_name="products")
    product = models.ForeignKey('merchants.Product', on_delete=models.DO_NOTHING)
    product_name = models.CharField(max_length=100)

    def __str__(self):
        return self.product_name

    class Meta:
        db_table = "merchant_promotion_products"


class MerchantPromotionTimeInterval(ScooterModel):
    """ Intervalos de tiempo que se aplicara la promoción """
    promotion = models.ForeignKey(MerchantPromotion, on_delete=models.DO_NOTHING, related_name="intervals_time")
    from_time = models.TimeField(null=True)
    to_time = models.TimeField(null=True)

    def __str__(self):
        return "De: {} a: {}".format(self.from_time, self.to_time)

    class Meta:
        db_table = "merchant_promotion_time_intervals"


class MerchantPromotionTimeScheduleInterval(ScooterModel):
    """ Dias en que la promoción es aplicable """
    promotion_interval = models.ForeignKey(MerchantPromotionTimeInterval, on_delete=models.DO_NOTHING,
                                           related_name="days")
    schedule = models.ForeignKey('common.Schedule', on_delete=models.DO_NOTHING)
    schedule_name = models.CharField(max_length=15)
    schedule_slug_name = models.CharField(max_length=15)

    def __str__(self):
        return self.schedule_name

    class Meta:
        db_table = "merchant_promotion_schedule_intervals"


class MerchantPromotionHistory(ScooterModel):
    """ Historial de promociones usadas """
    promotion = models.ForeignKey(MerchantPromotion, on_delete=models.DO_NOTHING, related_name="days")
    station = models.ForeignKey('stations.Station', on_delete=models.DO_NOTHING)
    order = models.ForeignKey('orders.Order', on_delete=models.DO_NOTHING)
    order_amount = models.FloatField()
    subtotal_order_amount = models.FloatField()
    discount = models.FloatField()
    customer = models.ForeignKey('customers.Customer', on_delete=models.DO_NOTHING)


class PromotionCustomerRequirements(ScooterModel):
    """ Requrimientos para aplicar la promoción a un cliente """
    pass
