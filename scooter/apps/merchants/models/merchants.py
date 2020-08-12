""" Merchants models """
# django
from django.contrib.gis.db import models
# Utilities
from scooter.utils.models import ScooterModel


class Merchant(ScooterModel):
    user = models.OneToOneField('users.User', on_delete=models.DO_NOTHING)
    contact_person = models.CharField(max_length=80)
    picture = models.ImageField(upload_to='merchants/pictures/', blank=True, null=True)
    merchant_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    # Config
    is_delivery_by_store = models.BooleanField(default=False)
    # Help
    information_is_complete = models.BooleanField(default=False)
    category = models.ForeignKey('common.CategoryMerchant', on_delete=models.DO_NOTHING)
    subcategory = models.ForeignKey('common.SubcategoryMerchant', on_delete=models.DO_NOTHING, null=True, blank=True)
    # stats
    reputation = models.FloatField(default=0)

    def __str__(self):
        return self.merchant_name


class MerchantSchedule(ScooterModel):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="schedules")
    schedule = models.ForeignKey('common.Schedule', on_delete=models.DO_NOTHING)
    from_hour = models.TimeField()
    to_hour = models.TimeField()

    class Meta:
        unique_together = ('merchant', 'schedule')


class MerchantAddress(ScooterModel):
    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE, related_name="address")
    full_address = models.CharField(max_length=300)
    references = models.CharField(max_length=150, blank=True, null=True)
    point = models.PointField(blank=True, null=True)


# For the clients of each merchant
class MemberMerchant(ScooterModel):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING)
    total_orders = models.PositiveIntegerField(default=0)
    total_orders_cancelled = models.PositiveIntegerField(default=0)
    first_order_date = models.DateTimeField(auto_now_add=True)
    last_order_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('merchant', 'customer')
        db_table = 'merchants_member_merchant'

    def __str__(self):
        return self.customer.name








