""" User models """

# Django
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
# Utilities
from scooter.utils.models import ScooterModel
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# Mixins
from django.contrib.auth.models import PermissionsMixin
# Managers
from scooter.apps.users.managers.users import CustomUserManager


class User(ScooterModel, AbstractBaseUser, PermissionsMixin):
    """ User models """
    CUSTOMER = 1
    STATION = 2
    DELIVERY_MAN = 3
    ADMIN = 4
    MERCHANT = 5
    ROLE_CHOICES = (
        (CUSTOMER, _('Cliente')),
        (STATION, _('Central')),
        (DELIVERY_MAN, _('Repartidor')),
        (ADMIN, _('Administrador')),
        (MERCHANT, _('Comerciante')),
    )
    username = models.CharField(
        unique=True,
        max_length=150,
        error_messages={
            'unique': 'Ya existe un usuario'
        })

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    is_client = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    auth_facebook = models.BooleanField(default=False)
    facebook_id = models.CharField(max_length=200, unique=True, blank=True, null=True)

    # Extends
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    # The verification deadline is two days after those days, if the user is not verified so
    # the user must request the forwarding code
    verification_deadline = models.DateTimeField()
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=CUSTOMER, null=True, blank=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def get_short_name(self):
        return self.username

    def is_customer(self):
        return self.role == self.CUSTOMER

    def is_station(self):
        return self.role == self.STATION

    def is_delivery_man(self):
        return self.role == self.DELIVERY_MAN

    def isAdmin(self):
        return self.role == self.ADMIN


class Contact(ScooterModel):
    name = models.CharField(max_length=60)
    email = models.EmailField()
    identify = models.CharField(max_length=50)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
