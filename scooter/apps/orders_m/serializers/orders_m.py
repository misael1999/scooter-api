# Rest framework
from django.conf import settings
from django.contrib.gis.geos import fromstr, Point
from django.utils import timezone
from rest_framework import serializers
# Serializers
from scooter.apps.common.serializers import OrderStatusModelSerializer, ServiceModelSerializer
from scooter.apps.common.serializers.common import Base64ImageField, MerchantFilteredPrimaryKeyRelatedField
from scooter.apps.customers.serializers import CustomerAddressModelSerializer, CustomerSimpleOrderSerializer, \
    PointSerializer
# Models
from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.delivery_men.serializers import DeliveryManOrderSerializer
from scooter.apps.merchants.models import Product
from scooter.apps.orders.models.ratings import RatingOrder
from scooter.apps.stations.models import Station, StationService
from scooter.apps.common.models import Service
from scooter.apps.customers.models import CustomerAddress
from scooter.apps.orders.models.orders import Order
# Django Geo
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
# Serializers primary field
from scooter.apps.common.serializers.common import CustomerFilteredPrimaryKeyRelatedField
from scooter.apps.stations.serializers import StationSimpleOrderSerializer


class DetailOrderMerchantSerializer(serializers.Serializer):
    product_id = MerchantFilteredPrimaryKeyRelatedField(queryset=Product.objects, source="product")
    quantity = serializers.IntegerField(min_value=1)
    # price_product


class OrderMerchantCurrentStatusSerializer(serializers.ModelSerializer):
    order_status = serializers.StringRelatedField()
    delivery_man = DeliveryManOrderSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('order_status', 'delivery_man')
        read_only_fields = fields


# For requests we must put all the fields as read only
class OrderMerchantModelSerializer(serializers.ModelSerializer):
    service = serializers.StringRelatedField(read_only=True, source="station_service")

    class Meta:
        model = Order
        fields = ("id",
                  'customer', 'merchant', 'member_station', 'member_merchant', 'delivery_man', 'station',
                  'service', 'station_service', 'merchant_location', 'to_address', 'service_price',
                  'order_price', 'total_order', 'indications', 'price_order', 'maximum_response_time',
                  'distance', 'date_delivered_order', 'order_date', 'is_delivery_by_store', 'qr_code',
                  'order_status', 'phone_number', 'in_process', 'is_safe_order', 'reason_rejection')


# For customer history orders
class OrderWithDetailSimpleSerializer(serializers.ModelSerializer):
    details = DetailOrderMerchantSerializer(many=True)
    service = serializers.StringRelatedField(read_only=True, source="station_service")
    # rated_order = RatingOrderSerializer(required=False, read_only=True)
    to_address = serializers.StringRelatedField(read_only=True)
    from_address = serializers.StringRelatedField(read_only=True)
    delivery_man = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ("id",
                  'customer', 'merchant', 'member_station', 'member_merchant', 'delivery_man', 'station',
                  'service', 'station_service', 'merchant_location', 'to_address', 'service_price',
                  'order_price', 'total_order', 'indications', 'price_order', 'maximum_response_time',
                  'distance', 'date_delivered_order', 'order_date', 'is_delivery_by_store', 'qr_code',
                  'order_status', 'phone_number', 'in_process', 'is_safe_order', 'reason_rejection')
        read_only_fields = fields


class OrderMerchantWithDetailModelSerializer(serializers.ModelSerializer):
    station = StationSimpleOrderSerializer(read_only=True, source="station")
    customer = CustomerSimpleOrderSerializer(read_only=True)
    from_address = CustomerAddressModelSerializer()
    to_address = CustomerAddressModelSerializer()
    service = serializers.StringRelatedField(read_only=True, source="station_service")
    # order_status = serializers.StringRelatedField(read_only=True)
    details = DetailOrderMerchantSerializer(many=True)
    delivery_man = DeliveryManOrderSerializer(required=False)
    order_status = OrderStatusModelSerializer(read_only=True)
    # rated_order = RatingOrderSerializer(required=False, read_only=True)

    class Meta:
        model = Order
        fields = ("id",
                  'customer', 'merchant', 'member_station', 'member_merchant', 'delivery_man', 'station',
                  'service', 'station_service', 'merchant_location', 'to_address', 'service_price',
                  'order_price', 'total_order', 'indications', 'price_order', 'maximum_response_time',
                  'distance', 'date_delivered_order', 'order_date', 'is_delivery_by_store', 'qr_code',
                  'order_status', 'phone_number', 'in_process', 'is_safe_order', 'reason_rejection')
        read_only_fields = fields
