""" Common status serializers """
# Django rest framework
import random
from string import ascii_uppercase, digits

from django.conf import settings
from rest_framework import serializers
# Models
from scooter.apps.orders.models import Order
from scooter.apps.orders.serializers.v2 import DetailOrderSerializer, DeliveryManOrderSerializer, \
    OrderStatusModelSerializer, CardModelSerializer
from scooter.apps.payments.models.cards import Card, CustomerConekta
# Utilities
from scooter.apps.stations.models import Station
from scooter.apps.support.models import Support, SupportMessage
from scooter.utils.serializers.scooter import ScooterModelSerializer


class OrderSupportSerializer(serializers.ModelSerializer):
    merchant = serializers.StringRelatedField(read_only=True)
    service = serializers.StringRelatedField(read_only=True, source="station_service")
    # order_status = serializers.StringRelatedField(read_only=True)
    details = DetailOrderSerializer(many=True)
    delivery_man = DeliveryManOrderSerializer(required=False)
    order_status = OrderStatusModelSerializer(read_only=True)
    card = CardModelSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ("id", 'merchant', "service",
                  "service_price", "distance",
                  "indications", "approximate_price_order", 'reason_rejection', 'date_update_order',
                  "order_date", "date_delivered_order", "qr_code", "order_status",
                  "customer", "delivery_man", "station", 'details', 'maximum_response_time', 'in_process',
                  'service_id', 'is_safe_order', 'station_object', 'merchant_location',
                  'order_price', 'total_order', 'is_delivery_by_store', 'is_order_to_merchant', 'is_payment_online',
                  'card'
                  )
        read_only_fields = fields


class SupportMessageSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = (
            'id',
            'text',
            'sender_by',
            'receiver_by',
            'viewed',
            'viewed_date',
            'support',
            'created'
        )
        read_only_fields = fields


class SupportModelSimpleSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    support_status = serializers.StringRelatedField(read_only=True)
    support_status_id = serializers.IntegerField(read_only=True)
    support_type = serializers.StringRelatedField(read_only=True)
    support_type_id = serializers.IntegerField(read_only=True)
    order = OrderSupportSerializer(read_only=True)

    # messages = SupportMessageSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Support
        fields = (
            'id',
            'sku',
            'issue',
            'is_to_order',
            'is_to_help',
            'is_to_delivery_man',
            'is_open',
            'support_type',
            'support_type_id',
            'finish_date',
            'order_sku',
            'order_details',
            'order',
            'delivery_man',
            'customer',
            'user',
            'station',
            'support_status',
            'support_status_id',
            'created',
            # 'messages'
        )
        read_only_fields = fields


def generate_sku():
    try:
        CODE_LENGTH = 10
        """ Handle code creation """
        pool = ascii_uppercase + digits
        sku = ''.join(random.choices(pool, k=CODE_LENGTH))
        while Support.objects.filter(sku=sku).exists():
            sku = ''.join(random.choices(pool, k=CODE_LENGTH))

        return sku
    except Exception as ex:
        raise ValueError('Error al generar el codigo qr')
