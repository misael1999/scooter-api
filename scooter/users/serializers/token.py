""" Custom token serializers """

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
# Utilities
from django.utils import timezone
# Models
from scooter.users.models import Customer, Station
# Serializers
from scooter.users.serializers.customers import CustomerUserModelSerializer
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
            raise serializers.ValidationError({'detail': 'Usuario no verificado'})

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
