""" Users serializers """
# Django rest framework
from rest_framework import serializers
from django.contrib.gis.geos import Point
# Models
from scooter.apps.common.models import DeliveryManStatus
from scooter.apps.delivery_men.models.delivery_men import DeliveryMan
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer
# Serializers
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
# Utilities
from scooter.apps.delivery_men.utils import send_notify_change_location
# Django channels
from asgiref.sync import async_to_sync


class DeliveryManModelSerializer(ScooterModelSerializer):

    class Meta:
        model = DeliveryMan
        geo_field = 'location'
        fields = '__all__'


class DeliveryManOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryMan
        fields = (
            'id',
            'station',
            'name',
            'phone_number',
            'picture',
            'reputation')
        read_only_fields = fields


class DeliveryManUserModelSerializer(ScooterModelSerializer):
    user = UserModelSimpleSerializer()

    class Meta:
        model = DeliveryMan
        fields = '__all__'
        read_only_fields = (
            'reputation',
        )


class UpdateLocationDeliverySerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    def update(self, instance, data):
        try:
            location = Point(x=data['longitude'], y=data['latitude'])
            instance.location = location
            instance.save()
            # send data through django channels
            async_to_sync(send_notify_change_location)(instance.station.id, instance.id, 'UPDATE_LOCATION')
            return instance
        except Exception as ex:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error al guardar la ubicación'})


class AvailabilityDeliverySerializer(serializers.Serializer):

    def update(self, instance, data):
        try:
            if instance.delivery_status.slug_name == 'available':
                status = DeliveryManStatus.objects.get(slug_name='out_service')
            else:
                status = DeliveryManStatus.objects.get(slug_name='available')

            instance.delivery_status = status
            instance.save()
            # send data through django channels
            async_to_sync(send_notify_change_location)(instance.station.id, instance.id, 'UPDATE_AVAILABILITY')
            return instance
        except Exception as ex:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error al cambiar la disponibilidad'})

