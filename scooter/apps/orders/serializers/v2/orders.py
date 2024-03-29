from django.conf import settings
from rest_framework import serializers
# Serializers
from scooter.apps.common.serializers import OrderStatusModelSerializer, ServiceModelSerializer
from scooter.apps.common.serializers.common import Base64ImageField
from scooter.apps.customers.serializers import CustomerAddressModelSerializer, CustomerSimpleOrderSerializer, \
    PointSerializer
# Models
from scooter.apps.delivery_men.serializers import DeliveryManOrderSerializer
from scooter.apps.merchants.models import Product
from scooter.apps.merchants.serializers import MerchantUserSimpleSerializer

from scooter.apps.orders.models.orders import Order
# Django Geo
from scooter.apps.orders.serializers import RatingOrderSerializer
from scooter.apps.payments.serializers import CardModelSerializer
from scooter.apps.stations.serializers import StationSimpleOrderSerializer
from scooter.apps.orders.models import OrderDetailMenu, OrderDetailMenuOption, OrderDetail
from scooter.utils.functions import return_money_user_manually
from scooter.utils.serializers.scooter import ScooterModelSerializer
import conekta
conekta.api_key = settings.CONEKTA_API_KEY
conekta.api_version = settings.CONEKTA_API_KEY


class DetailMenuOptionSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = OrderDetailMenuOption
        fields = ('id', 'option', 'option_name', 'price_option', 'quantity')
        read_only_fields = ('id', 'option_name', 'price_option')


class DetailMenuSerializer(serializers.ModelSerializer):

    options = DetailMenuOptionSerializer(many=True)

    class Meta:
        model = OrderDetailMenu
        fields = ("id", 'menu', 'menu_name', 'options')
        read_only_fields = ('id', 'menu_name')


class DetailOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(max_length=201, allow_null=True, required=False)
    product_price = serializers.FloatField(required=False)
    picture = Base64ImageField(required=False, use_url=True, allow_null=True, allow_empty_file=True, max_length=None)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product", allow_null=True,
                                                    required=False)
    menu_options = DetailMenuSerializer(many=True, required=False, allow_null=True)
    total_detail = serializers.FloatField(required=False, source="get_total_detail")
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = OrderDetail
        fields = ('id', 'product_name', 'product_price', 'quantity',
                  'picture', 'product_id', 'menu_options', 'total_detail'
                  )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class OrderWithoutInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ("id", "to_address", "order_date", "date_delivered_order",
                  "qr_code", "order_status", 'order_price', 'date_update_order'
                  )
        read_only_fields = fields


class OrderWithDetailModelSerializer(ScooterModelSerializer):
    merchant = MerchantUserSimpleSerializer()
    station = serializers.StringRelatedField(read_only=True)
    station_object = StationSimpleOrderSerializer(read_only=True, source="station")
    customer = CustomerSimpleOrderSerializer(read_only=True)
    from_address = CustomerAddressModelSerializer()
    to_address = CustomerAddressModelSerializer()
    # order_status = serializers.StringRelatedField(read_only=True)
    service = serializers.StringRelatedField(read_only=True, source="station_service")
    service_obj = ServiceModelSerializer(read_only=True, source="service")
    details = DetailOrderSerializer(many=True)
    delivery_man = DeliveryManOrderSerializer(required=False)
    order_status = OrderStatusModelSerializer(read_only=True)
    rated_order = RatingOrderSerializer(required=False, read_only=True)
    card = CardModelSerializer(read_only=True)
    supports = serializers.SerializerMethodField('get_supports', read_only=True)

    def get_supports(self, order):
        qs = order.supports.filter(is_open=True).values_list('id', flat=True)
        return qs

    class Meta:
        model = Order
        fields = ("id", 'merchant', "service", 'service_obj',
                  "from_address", "to_address", "service_price", "distance",
                  "indications", "approximate_price_order", 'reason_rejection', 'date_update_order',
                  "order_date", "date_delivered_order", "qr_code", "order_status",
                  "customer", "delivery_man", "station", 'details', 'maximum_response_time', 'validate_qr',
                  'rated_order', 'in_process', 'service_id', 'is_safe_order', 'station_object', 'merchant_location',
                  'order_price', 'total_order', 'is_delivery_by_store', 'is_order_to_merchant', 'is_payment_online',
                  'card', 'increment_price_operating', 'has_rate_operating', 'supports'
                  )
        read_only_fields = fields


class ReturnOrderMoneySerializer(serializers.Serializer):
    def update(self, order, data):
        try:
            return_money_user_manually(order)
            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in return order money, please check it")
            print(ex.args.__str__())
            print(ex.__cause__)
            print(ex)
            raise serializers.ValidationError({'detail': 'Error al devolver el dinero de la orden'})


class ConfirmOrderMoneySerializer(serializers.Serializer):
    def update(self, order, data):
        try:
            order_conekta = conekta.Order.find(order.order_conekta_id)
            order_captured = order_conekta.capture()
            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in confirm order money, please check it")
            print(ex.args.__str__())
            print(ex.__cause__)
            print(ex)
            raise serializers.ValidationError({'detail': 'Error al confirmar el dinero de la orden'})
