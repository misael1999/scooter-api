# django
from django.contrib.gis.db import models
# Utilities
from django.core.validators import RegexValidator
from scooter.utils.models.scooter import ScooterModel


class Customer(ScooterModel):
    user = models.OneToOneField('users.User', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=150)
    birthdate = models.DateField(blank=True, null=True)
    picture = models.ImageField(upload_to='customers/pictures/', blank=True, null=True)
    picture_url = models.CharField(max_length=300, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_safe_user = models.BooleanField(default=False)

    # stats
    reputation = models.FloatField(default=0)

    def __str__(self):
        return '{name}'.format(name=self.name)


class CustomerAddress(ScooterModel):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    alias = models.CharField(max_length=30)
    full_address = models.CharField(max_length=350)
    exterior_number = models.CharField(max_length=10, blank=True, null=True)
    inside_number = models.CharField(max_length=10, blank=True, null=True, )
    references = models.CharField(max_length=150, blank=True, null=True)
    point = models.PointField(blank=True, null=True)
    type_address = models.ForeignKey('common.TypeAddress', on_delete=models.DO_NOTHING,
                                     default=1)

    class Meta:
        db_table = 'customers_customer_address'

    def __str__(self):
        return self.full_address



