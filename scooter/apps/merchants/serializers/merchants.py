""" Merchants serializers """
# General
from datetime import timedelta
from django.utils import timezone
# Django
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import IntegrityError
# Django rest framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# Models
from scooter.apps.merchants.models import Merchant
from scooter.apps.users.models import User
from scooter.apps.stations.models.stations import Station, StationAddress, StationSchedule, StationService
from scooter.apps.common.models import Service, Schedule, CategoryMerchant, SubcategoryMerchant
# Utilities
from scooter.utils.functions import send_mail_verification, generate_verification_token
# Serializers
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
from scooter.apps.common.serializers import Base64ImageField


class MerchantWithAllInfoSerializer(serializers.ModelSerializer):

    category = serializers.StringRelatedField(read_only=True)
    subcategory = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Merchant
        fields = ('id', 'contact_person', 'picture', 'merchant_name', 'phone_number', 'is_delivery_by_store',
                  'information_is_complete', 'category', 'subcategory', 'reputation'),
        read_only_fields = fields


# Create a new merchant
class MerchantSignUpSerializer(serializers.Serializer):
    """ Serializer only to register a new merchant """
    username = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='El email ya esta en uso')])

    contact_person = serializers.CharField(max_length=60)
    password = serializers.CharField(min_length=8, max_length=64)
    phone_number = serializers.CharField(max_length=15)
    category_id = serializers.PrimaryKeyRelatedField(queryset=CategoryMerchant.objects.all(), source="category")
    subcategory_id = serializers.PrimaryKeyRelatedField(queryset=SubcategoryMerchant.objects.all(),
                                                        source="subcategory",
                                                        required=False, allow_null=True)
    merchant_name = serializers.CharField(max_length=100, validators=[UniqueValidator(
        queryset=Merchant.objects.all(),
        message='Ya existe un negocio con el mismo nombre. ¿El negocio es tuyo?,'
                ' comunicate con nosotros scooterenvios@gmail.com')])

    def create(self, data):
        try:
            user = User(username=data.pop('username'),
                        is_verified=True,
                        role=User.MERCHANT,
                        is_client=False,
                        verification_deadline=timezone.localtime(timezone.now()) + timedelta(days=2))

            password = data.pop('password')
            user.set_password(password)
            user.save()
            merchant = Merchant.objects.create(**data,
                                               user=user)

            # code = generate_verification_token(user=user,
            #                                    exp=timezone.localtime(timezone.now()) + timedelta(minutes=20),
            #                                    token_type='email_confirmation')

            subject = 'Bienvenido {name}'.format(name=merchant.merchant_name)
            data = {
                'email': user.username,
                'name': merchant.merchant_name,
                'password': password,
                'url': settings.URL_SERVER_FRONTEND
            }
            send_email = send_mail_verification(subject=subject,
                                                to_user=user.username,
                                                path_template="emails/merchants/welcome.html",
                                                data=data)
            if not send_email:
                raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar el correo'})
            return user

        except Exception as ex:
            return serializers.ValidationError({'detail': 'Ha ocurrido un problema al registrarse'})
