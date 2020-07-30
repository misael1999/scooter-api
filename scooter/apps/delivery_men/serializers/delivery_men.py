""" Users serializers """
# Django rest framework
from django.utils import timezone
from rest_framework import serializers
from django.contrib.gis.geos import Point
# Models
from scooter.apps.common.models import DeliveryManStatus
from scooter.apps.common.serializers import Base64ImageField
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
    picture = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = DeliveryMan
        geo_field = 'location'
        fields = '__all__'
        read_only_fields = (
            'user', 'station', 'name', 'last_name',
            'phone_number', 'total_orders', 'reputation', 'location',
            'delivery_status'
        )

    def update(self, instance, data):
        """ Before updating we have to delete the previous image """
        try:
            if data['picture']:
                instance.picture.delete(save=True)
        except Exception as ex:
            print("Exception deleting image delivery man, please check it")
            print(ex.args.__str__())
        return super().update(instance, data)


class DeliveryManOrderSerializer(serializers.ModelSerializer):

    picture = Base64ImageField(use_url=True)

    class Meta:
        model = DeliveryMan
        geofield = 'location'
        fields = (
            'id',
            'station',
            'picture',
            'name',
            'phone_number',
            'reputation',
            'location',
        )
        read_only_fields = fields


class DeliveryManUserModelSerializer(ScooterModelSerializer):
    user = UserModelSimpleSerializer()
    picture = Base64ImageField(use_url=True)

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
            instance.last_time_update_location = timezone.localtime(timezone.now())
            instance.save()
            # send data through django channels
            # async_to_sync(send_notify_change_location)(instance.station.id, instance.id, 'UPDATE_LOCATION')
            return instance
        except Exception as ex:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error al guardar la ubicación'})


class AvailabilityDeliverySerializer(serializers.Serializer):

    status = serializers.SlugRelatedField(slug_field="slug_name", queryset=DeliveryManStatus.objects.all())

    def update(self, instance, data):
        try:
            status = data['status']

            if status.slug_name == 'available':
                status_availability = True
            else:
                status_availability = False

            instance.delivery_status = status
            instance.save()
            # send data through django channels
            # async_to_sync(send_notify_change_location)(instance.station.id, instance.id, 'UPDATE_AVAILABILITY')
            return status_availability
        except Exception as ex:
            print(ex.args)
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error al cambiar la disponibilidad'})
