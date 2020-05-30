# django
from django.contrib.gis.db import models
# Utilities
from scooter.utils.models import ScooterModel
from django.core.validators import RegexValidator


class DeliveryMan(ScooterModel):
    user = models.OneToOneField('users.User', on_delete=models.DO_NOTHING)
    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='El numero de telefono debe ser ingresado con el formato: +23856671672. Hasta 15 digitos permitidos'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=20, blank=True, null=True)
    picture = models.ImageField(upload_to='customers/pictures/', blank=True, null=True)
    salary_per_order = models.FloatField(default=0)

    # stats
    total_orders = models.PositiveIntegerField(default=0)
    reputation = models.FloatField(default=0)
    location = models.PointField(blank=True, null=True)

    class Meta:
        db_table = 'delivery_men_delivery_man'

    def __str__(self):
        return self.name