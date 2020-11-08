# django
from django.contrib.gis.db import models
# Utilities
from scooter.utils.models import ScooterModel
from django.core.validators import RegexValidator


class DeliveryMan(ScooterModel):
    user = models.OneToOneField('users.User', on_delete=models.DO_NOTHING)
    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE, null=True, blank=True)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.DO_NOTHING, null=True, blank=True)
    name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='El numero de telefono debe ser ingresado con el formato: +23856671672. Hasta 15 digitos permitidos'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=20, blank=True, null=True)
    picture = models.ImageField(upload_to='deliveryman/pictures/', blank=True, null=True)
    # stats
    reputation = models.FloatField(default=0)
    location = models.PointField(blank=True, null=True, geography=True)
    delivery_status = models.ForeignKey('common.DeliveryManStatus', on_delete=models.DO_NOTHING, default=1)
    last_time_update_location = models.DateTimeField(null=True, blank=True)
    # Vehicle data
    vehicle_plate = models.CharField(max_length=10, null=True, blank=True)
    vehicle_model = models.CharField(max_length=30, null=True, blank=True)
    vehicle_year = models.CharField(max_length=10, null=True, blank=True)
    vehicle_color = models.CharField(max_length=15, null=True, blank=True)
    vehicle_type = models.ForeignKey('common.TypeVehicle', on_delete=models.DO_NOTHING, default=1)

    from_merchant = models.BooleanField(default=False)

    class Meta:
        db_table = 'delivery_men_delivery_man'

    def __str__(self):
        return self.name


class DeliveryManAddress(ScooterModel):
    delivery_man = models.OneToOneField(DeliveryMan, on_delete=models.CASCADE, related_name='address')
    street = models.CharField(max_length=100, blank=True, null=True)
    suburb = models.CharField(max_length=60, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    exterior_number = models.CharField(max_length=10, blank=True)
    inside_number = models.CharField(max_length=10, blank=True, null=True)
    references = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = 'delivery_man_address'

    def __str__(self):
        return self.street

