# django
from django.db import models
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