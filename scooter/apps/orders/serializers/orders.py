# Rest framework
from rest_framework import serializers
# models
from scooter.apps.orders.models.orders import (Order, OrderDetail)
# Serializers
from scooter.apps.common.serializers.common import Base64ImageField
# Models
from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.stations.models import Station, StationService
from scooter.apps.common.models import Service
from scooter.apps.customers.models import CustomerAddress
from scooter.apps.orders.models.orders import Order


# For requests we must put all the fields as read only
class OrderModelSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(source='created')

    class Meta:
        model = Order
        fields = ("customer", "delivery_man", "station", "service",
                  "from_address_id", "to_address_id", "service_price",
                  "indications", "approximate_price_order",
                  "date_delivered_order", "qr_code", "order_status", "order_date")
        read_only_fields = ("customer", "delivery_man", "station", "service",
                            "from_address_id", "to_address_id", "service_price",
                            "indications", "approximate_price_order",
                            "date_delivered_order", "qr_code", "order_status", "order_date")


class DetailOrderSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=60)
    picture = Base64ImageField(required=False)


# For create a new order
class CreateOrderSerializer(serializers.Serializer):
    details = DetailOrderSerializer(many=True)
    station_id = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(), source="station")
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="service")
    from_address_id = serializers.PrimaryKeyRelatedField(queryset=CustomerAddress.objects.all(), source="from_address")
    to_address_id = serializers.PrimaryKeyRelatedField(queryset=CustomerAddress.objects.all(), source="from_address")
    service_price = serializers.FloatField()
    indications = serializers.CharField(max_length=300, required=False)
    approximate_price_order = serializers.FloatField()

    def validate(self, data):

        # Check if the station has the requested service
        exist_service = StationService.objects.filter(station=data['station'], service=data['service']).exists()
        if not exist_service:
            raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})

        # Add customer of the context in object data
        data['customer'] = self.context['customer']
        return data

    def create(self, data):
        try:
            details = data.pop('details', None)
            order = Order.objects.create(**data)

            # Save detail order
            details_to_save = [OrderDetail(**detail, order=order) for detail in details]
            OrderDetail.objects.bulk_create(details_to_save)

            # Check if the station has manual assignment activated

            # Send push notification to station or delivery man

            return order
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as ex:
            print("Exception in create order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al crear la orden'})
