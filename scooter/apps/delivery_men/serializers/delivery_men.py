""" Users serializers """
# Django rest framework
from rest_framework import serializers
from django.contrib.gis.geos import Point
# Models
from scooter.apps.delivery_men.models.delivery_men import DeliveryMan
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer
# Serializers
from scooter.apps.users.serializers.users import UserModelSimpleSerializer


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
            return instance
        except Exception as ex:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error al guardar la ubicación'})