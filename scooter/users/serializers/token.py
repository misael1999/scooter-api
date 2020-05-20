""" Custom token serializers """

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
# Utilities
from django.utils import timezone
# Models
from scooter.users.models import Customer, Station
from scooter.delivery_men.models import DeliveryMen
# Serializers
from scooter.users.serializers.customers import CustomerUserModelSerializer
from scooter.delivery_men.serializers.delivery_men import DeliveryManUserModelSerializer
from scooter.users.serializers.stations import StationUserModelSerializer


class StationTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {'no_active_account': 'Usuario o contraseña incorrectos'}

    def validate(self, attrs):
        data = super().validate(attrs)
        try:
            station = self.user.station
        except Station.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No tienes permisos para iniciar sesión'})

        if not self.user.is_verified:
            raise serializers.ValidationError({'detail': 'Es necesario que verifique su correo electronico {email}'.
                                              format(email=self.user.username)})

        data['station'] = StationUserModelSerializer(station).data
        # Add extra responses here
        # data['user'] = UserModelSerializer(self.user).data
        return data


class CustomerTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {'no_active_account': 'Usuario o contraseña incorrectos'}

    def validate(self, attrs):
        data = super().validate(attrs)
        # Users can validate their account two days later
        try:
            customer = self.user.customer
        except Customer.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No tienes permisos para iniciar sesión'})

        if timezone.now() > self.user.verification_deadline and not self.user.is_verified:
            raise serializers.ValidationError({'detail': 'Ha expirado su tiempo de verificación'})

        data['user'] = CustomerUserModelSerializer(customer).data

        # Add extra responses here
        # data['user'] = UserModelSerializer(self.user).data
        return data


class DeliveryManTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {'no_active_account': 'Télefono o contraseña incorrectos'}

    def validate(self, attrs):
        # Delivery man can validate their account
        data = super().validate(attrs)
        try:
            delivery_man = self.user.deliverymen
        except DeliveryMen.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No tienes permisos para iniciar sesión'})

        data['user'] = DeliveryManUserModelSerializer(delivery_man).data

        # Add extra responses here
        # data['user'] = UserModelSerializer(self.user).data
        return data
