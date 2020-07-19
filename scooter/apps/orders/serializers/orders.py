# Rest framework
from django.contrib.gis.geos import fromstr
from rest_framework import serializers
# Serializers
from scooter.apps.common.serializers import OrderStatusModelSerializer
from scooter.apps.common.serializers.common import Base64ImageField
from scooter.apps.customers.serializers import CustomerAddressModelSerializer, CustomerSimpleOrderSerializer
# Models
from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.delivery_men.serializers import DeliveryManOrderSerializer
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


class RatingOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = RatingOrder
        fields = ("order", "station", "delivery_man",
                  "rating_customer", "comments", "rating")
        read_only_fields = fields


class DetailOrderSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=60)
    picture = Base64ImageField(required=False, use_url=True, allow_null=True, allow_empty_file=True, max_length=None)


class OrderCurrentStatusSerializer(serializers.ModelSerializer):
    order_status = serializers.StringRelatedField()
    delivery_man = DeliveryManOrderSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('order_status', 'delivery_man')
        read_only_fields = fields


# For requests we must put all the fields as read only
class OrderModelSerializer(serializers.ModelSerializer):
    service = serializers.StringRelatedField(read_only=True, source="station_service")

    class Meta:
        model = Order
        fields = ("id", "delivery_man", "station", "service", "distance",
                  "from_address_id", "to_address_id", "service_price",
                  "indications", "approximate_price_order", 'maximum_response_time',
                  "date_delivered_order", "qr_code", "order_status", "order_date", 'validate_qr')


# For customer history orders
class OrderWithDetailSimpleSerializer(serializers.ModelSerializer):
    details = DetailOrderSerializer(many=True)
    delivery_man = DeliveryManOrderSerializer(required=False)
    service = serializers.StringRelatedField(read_only=True, source="station_service")
    rated_order = RatingOrderSerializer(required=False, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "service",
                  "from_address", "to_address", "service_price", "distance",
                  "indications", "approximate_price_order", 'reason_rejection',
                  "order_date", "date_delivered_order", "qr_code", "order_status",
                  "customer", "delivery_man", "station", 'details', 'maximum_response_time',
                  'validate_qr', 'rated_order', 'in_process')
        read_only_fields = fields


class OrderWithDetailModelSerializer(serializers.ModelSerializer):
    station = serializers.StringRelatedField(read_only=True)
    customer = CustomerSimpleOrderSerializer(read_only=True)
    from_address = CustomerAddressModelSerializer()
    to_address = CustomerAddressModelSerializer()
    service = serializers.StringRelatedField(read_only=True, source="station_service")
    # order_status = serializers.StringRelatedField(read_only=True)
    details = DetailOrderSerializer(many=True)
    delivery_man = DeliveryManOrderSerializer(required=False)
    order_status = OrderStatusModelSerializer(read_only=True)
    rated_order = RatingOrderSerializer(required=False, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "service",
                  "from_address", "to_address", "service_price", "distance",
                  "indications", "approximate_price_order", 'reason_rejection',
                  "order_date", "date_delivered_order", "qr_code", "order_status",
                  "customer", "delivery_man", "station", 'details', 'maximum_response_time', 'validate_qr',
                  'rated_order', 'in_process')
        read_only_fields = fields


class CalculateServicePriceSerializer(serializers.Serializer):
    """ Calculate the price of the service before requesting the service """
    from_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects.all(),
                                                             source="from_address")
    to_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects.all(),
                                                           source="to_address")
    station_id = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(), source="station")
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="service")

    def validate(self, data):
        # Check if the station has the requested service
        try:
            station = data['station']
            exist_service = station.services.get(service=data['service'])
            # if not exist_service:
            #     raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})
            data['station_service'] = exist_service
            data.pop('service')
        except StationService.DoesNotExist:
            raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})

        return data

    def create(self, data):
        try:
            data_service = calculate_service_price(from_address=data['from_address'],
                                                   to_address=data['to_address'],
                                                   service=data['station_service'])
            return data_service['price_service']
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al consultar precio de la orden'})


# Methods helpers
def get_nearest_delivery_man(location_selected, station, list_exclude, distance):
    """ Get nearest delivery man and exclude who are in the history of rejected orders """

    # List of delivery men nearest
    delivery_man = DeliveryMan.objects. \
        exclude(id__in=list_exclude). \
        filter(status__slug_name="active", station=station,
               location__distance_lte=(
                   location_selected.point,
                   D(km=distance))) \
        .annotate(distance=Distance('location', location_selected.point)) \
        .order_by('distance').first()
    # delivery_man = DeliveryMan.objects.filter(station=station,
    #                                           location__distance_lte=(
    #                                               location_selected.point, D(km=distance))
    #                                           ).exclude(id__in=list_exclude).last()

    return delivery_man


def calculate_service_price(from_address, to_address, service):
    try:
        # from_address = data['from_address']
        # to_address = data['to_address']
        # longitude position 0 and latitude position 1
        # from_point = (from_address.point[1], from_address.point[0])
        # to_point = (to_address.point[1], to_address.point[0])
        pnt = fromstr(
            from_address.point, srid=4326
        ).transform(3857, clone=True)
        pnt1 = fromstr(
            to_address.point, srid=4326
        ).transform(3857, clone=True)
        distance_points = (pnt.distance(pnt1) / 1000)
        distance_points = distance_points + (distance_points * 0.30)
        # distance_points = distance.vincenty(from_point, to_point).kilometers
        # distance_points = distance_points + (distance_points * 0.45)

        # service = data['station_service']
        price_service = 0.0
        # If the distance is less than one kilometer from the base rate price,
        # then the service price is equal to the base rate price
        if distance_points <= service.to_kilometer:
            price_service = service.base_rate_price
        else:
            # Verify how to much kilometers left and after multiply for the price kilomers ans
            kilometers_left = distance_points - service.to_kilometer
            price_service = service.base_rate_price + (kilometers_left * service.price_kilometer)
        return {'price_service': price_service, 'distance': distance_points}
    except ValueError as e:
        print(e)
        raise ValueError('Error al consultar precio de la orden')
    except Exception as ex:
        print(ex)
        raise ValueError('Error al consultar precio de la orden')
