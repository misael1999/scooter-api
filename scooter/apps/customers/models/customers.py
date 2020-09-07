# django
from django.contrib.gis.db import models
# Utilities
from django.core.validators import RegexValidator
from scooter.utils.models.scooter import ScooterModel


class Customer(ScooterModel):
    user = models.OneToOneField('users.User', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=150, null=True, blank=True)
    birthdate = models.DateField(blank=True, null=True)
    picture = models.ImageField(upload_to='customers/pictures/', blank=True, null=True)
    picture_url = models.CharField(max_length=300, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_safe_user = models.BooleanField(default=False)
    code_share = models.CharField(max_length=10, null=True)
    code_used = models.BooleanField(default=False)
    code_used_complete = models.BooleanField(default=False)
    # stats
    reputation = models.FloatField(default=0)

    def __str__(self):
        return '{name}'.format(name=self.name)


class CustomerAddress(ScooterModel):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    alias = models.CharField(max_length=100)
    full_address = models.CharField(max_length=350)
    category = models.CharField(blank=True, null=True, max_length=40)
    exterior_number = models.CharField(max_length=10, blank=True, null=True)
    inside_number = models.CharField(max_length=10, blank=True, null=True)
    references = models.CharField(max_length=150, blank=True, null=True)
    point = models.PointField(blank=True, null=True)
    type_address = models.ForeignKey('common.TypeAddress', on_delete=models.DO_NOTHING,
                                     default=1)

    class Meta:
        db_table = 'customers_customer_address'

    def __str__(self):
        return self.full_address


class HistoryCustomerInvitation(ScooterModel):

    code = models.CharField(max_length=50,
                            unique=True,
                            help_text="Code the customer issued by")

    issued_by = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE,
        help_text='Customer that is providing the invitation',
        related_name='issued_by'
    )
    used_by = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE,
        null=True,
        help_text='User that used the code to order'
    )

    used_used_by = models.BooleanField(default=False, help_text="Already used by use enter code promo")

    date = models.DateTimeField()
    is_pending = models.BooleanField(default=True)

    class Meta:
        db_table = 'customers_customer_history_invitation'


class CustomerPromotion(ScooterModel):

    name = models.CharField(max_length=70, null=True, blank=True)
    description = models.CharField(max_length=150, null=True, blank=True)
    history = models.ForeignKey(HistoryCustomerInvitation, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey('customers.Customer', on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField()
    expiration_date = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'customers_customer_promotions'
