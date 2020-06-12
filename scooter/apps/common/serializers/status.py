""" Common status serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.models.status import Status
from scooter.apps.common.models.orders import OrderStatus


class StatusModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = ('id', 'name', 'slug_name')


class OrderStatusModelSerializer(serializers.ModelSerializer):
    type_service = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderStatus
        fields = ('id', 'name', 'slug_name', 'type_service')
