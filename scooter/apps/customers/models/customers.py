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
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='El numero de telefono debe ser ingresado con el formato: +23856671672. Hasta 15 digitos permitidos'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=20, blank=True, null=True)

    # stats
    reputation = models.FloatField(default=0)

    def __str__(self):
        return '{name}'.format(name=self.name)


class CustomerAddress(ScooterModel):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    alias = models.CharField(max_length=30)
    street = models.CharField(max_length=100)
    suburb = models.CharField(max_length=60)
    postal_code = models.CharField(max_length=10)
    exterior_number = models.CharField(max_length=10)
    inside_number = models.CharField(max_length=10, blank=True, null=True)
    references = models.CharField(max_length=150)
    point = models.PointField(blank=True, null=True)

    class Meta:
        db_table = 'users_customer_address'

    def __str__(self):
        return self.alias



