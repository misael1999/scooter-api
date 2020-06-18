""" Common status serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.models.orders import OrderStatus


class OrderStatusSerializer(serializers.ModelSerializer):
    type_service = serializers.StringRelatedField()

    class Meta:
        model = OrderStatus
        fields = ('id', 'name', 'slug_name', 'type_service')
        read_only_fields = ('id', 'name', 'slug_name', 'type_service')

