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

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def get_short_name(self):
        return self.username
