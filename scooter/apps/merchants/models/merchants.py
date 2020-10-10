""" Merchants models """
# django
from django.contrib.gis.db import models
# Utilities
from django.core.validators import FileExtensionValidator

from scooter.utils.models import ScooterModel


class TypeMenuMerchant(ScooterModel):
    name = models.CharField(max_length=30)
    slug_name = models.CharField(max_length=30)


class Merchant(ScooterModel):
    user = models.OneToOneField('users.User', on_delete=models.DO_NOTHING)
    contact_person = models.CharField(max_length=80)
    picture = models.ImageField(upload_to='merchants/pictures/', blank=True, null=True,
                                validators=[FileExtensionValidator(['jpg', 'png', 'jpeg'])])
    merchant_name = models.CharField(max_length=100)
    description = models.CharField(max_length=120, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    # Config
    is_delivery_by_store = models.BooleanField(default=False)
    # Help
    information_is_complete = models.BooleanField(default=False)
    category = models.ForeignKey('common.CategoryMerchant', on_delete=models.DO_NOTHING)
    subcategory = models.ForeignKey('common.SubcategoryMerchant', on_delete=models.DO_NOTHING, null=True, blank=True)
    approximate_preparation_time = models.CharField(max_length=10, null=True)
    from_preparation_time = models.FloatField(default=0)
    to_preparation_time = models.FloatField(default=0)
    full_address = models.TextField(blank=True, null=True)
    # stats
    total_grades = models.IntegerField(default=0)
    reputation = models.FloatField(default=0)
    point = models.PointField(blank=True, null=True, srid=4326)
    is_open = models.BooleanField(default=False)
    rate = models.FloatField(default=3.0)
    type_menu = models.ForeignKey(TypeMenuMerchant,
                                  on_delete=models.DO_NOTHING,
                                  null=True, blank=True, default=1)
    area = models.ForeignKey('common.Area', default=1, on_delete=models.DO_NOTHING)
    zone = models.ForeignKey('common.Zone', blank=True, null=True, on_delete=models.DO_NOTHING)
    is_delivery_free = models.BooleanField(default=False)

    def __str__(self):
        return self.merchant_name


class MerchantSchedule(ScooterModel):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="schedules")
    schedule = models.ForeignKey('common.Schedule', on_delete=models.DO_NOTHING)
    from_hour = models.TimeField()
    to_hour = models.TimeField()

    class Meta:
        ordering = ['schedule_id']
        unique_together = ('merchant', 'schedule')


class MerchantAddress(ScooterModel):
    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE, related_name="address")
    full_address = models.CharField(max_length=300, null=True, blank=True)
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








