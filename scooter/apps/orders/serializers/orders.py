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
from scooter.apps.merchants.models import Product, Merchant
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


class RatingOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = RatingOrder
        fields = ("order", "station", "delivery_man",
                  "rating_customer", "comments", "rating")
        read_only_fields = fields


class DetailOrderSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=201, allow_null=True, required=False)
    picture = Base64ImageField(required=False, use_url=True, allow_null=True, allow_empty_file=True, max_length=None)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product", allow_null=True,
                                                    required=False)
    quantity = serializers.IntegerField(min_value=1, allow_null=True, required=True)


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
                  "date_delivered_order", "qr_code", "order_status", "order_date", 'validate_qr',
                  'is_safe_order', 'merchant_location',
                  'order_price', 'total_order', 'is_delivery_by_store', 'is_order_to_merchant')


# For customer history orders
class OrderWithDetailSimpleSerializer(serializers.ModelSerializer):
    details = DetailOrderSerializer(many=True)
    service = serializers.StringRelatedField(read_only=True, source="station_service")
    rated_order = RatingOrderSerializer(required=False, read_only=True)
    to_address = serializers.StringRelatedField(read_only=True)
    from_address = serializers.StringRelatedField(read_only=True)
    delivery_man = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ("id", "service",
                  "from_address", "to_address", "service_price", "distance",
                  "indications", "approximate_price_order", 'reason_rejection',
                  "order_date", "date_delivered_order", "qr_code", "order_status",
                  "customer", "delivery_man", "station", 'details', 'maximum_response_time',
                  'validate_qr', 'rated_order', 'in_process', 'is_safe_order', 'merchant_location',
                  'order_price', 'total_order', 'is_delivery_by_store', 'is_order_to_merchant')
        read_only_fields = fields


class OrderWithDetailModelSerializer(serializers.ModelSerializer):
    station = serializers.StringRelatedField(read_only=True)
    station_object = StationSimpleOrderSerializer(read_only=True, source="station")
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
                  'rated_order', 'in_process', 'service_id', 'is_safe_order', 'station_object', 'merchant_location',
                  'order_price', 'total_order', 'is_delivery_by_store', 'is_order_to_merchant',
                  )
        read_only_fields = fields


class CalculateServicePriceSerializer(serializers.Serializer):
    """ Calculate the price of the service before requesting the service """
    from_address_id = serializers.PrimaryKeyRelatedField(queryset=CustomerAddress.objects.all(),
                                                         source="from_address", required=False,
                                                         allow_null=True, allow_empty=True)
    to_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects,
                                                           source="to_address", required=False, allow_null=True)
    station_id = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(), source="station")
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="service")
    merchant_id = serializers.PrimaryKeyRelatedField(queryset=Merchant.objects.all(), source="merchant")
    is_order_to_merchant = serializers.BooleanField(default=False)
    point = PointSerializer(required=False, allow_null=True)
    is_current_location = serializers.BooleanField(required=False, allow_null=True)

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
            station = data['station']
            merchant = data.get('merchant', None)
            to_address = None
            from_address = None
            is_order_to_merchant = data.get('is_order_to_merchant', False)
            if is_free_order(station):
                return 0.0

            if is_order_to_merchant:
                from_address = merchant.point
            else:
                from_address = from_address=data['from_address'].point

            is_current_location = data.get('is_current_location', False)
            point = data.pop('point', None)
            if is_current_location:
                point = Point(x=point['lng'], y=point['lat'], srid=4326)
                to_address = None
            else:
                to_address = data['to_address'].point

            data_service = calculate_service_price(from_address,
                                                   to_address=to_address,
                                                   service=data['station_service'],
                                                   is_current_location=is_current_location,
                                                   point=point)
            return round(data_service['price_service'])
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al consultar precio de la orden'})


def is_free_order(station):
    is_free = False
    if station.free_orders_activated:
        current_hour = timezone.localtime(timezone.now()).strftime('%H:%M:%S')
        # import pdb; pdb.set_trace()
        if current_hour >= str(station.from_hour_free_order) and current_hour <= str(station.to_hour_free_order):
            is_free = True

    return is_free


# Methods helpers
def get_nearest_delivery_man(location_selected, station, list_exclude, distance, status):
    """ Get nearest delivery man and exclude who are in the history of rejected orders """

    # List of delivery men nearest

    # location__distance_lte = (
    #     location_selected.point,
    #     D(km=distance))

    SEARCH_NUMBER_DELIVERY = settings.SEARCH_NUMBER_DELIVERY
    delivery_man = DeliveryMan.objects. \
        exclude(id__in=list_exclude). \
        filter(status__slug_name="active", delivery_status__slug_name__in=status, station=station) \
        .annotate(distance=Distance('location', location_selected)) \
        .order_by('distance')[:SEARCH_NUMBER_DELIVERY]
    # delivery_man = DeliveryMan.objects.filter(station=station,
    #                                           location__distance_lte=(
    #                                               location_selected.point, D(km=distance))
    #                                           ).exclude(id__in=list_exclude).last()

    return delivery_man


def calculate_service_price(from_address, to_address, service, is_current_location, point):
    try:
        # from_address = data['from_address']
        # to_address = data['to_address']
        # longitude position 0 and latitude position 1
        # from_point = (from_address.point[1], from_address.point[0])
        # to_point = (to_address.point[1], to_address.point[0])

        if is_current_location:
            to_point = point
        else:
            to_point = to_address

        pnt = fromstr(
            from_address, srid=4326
        ).transform(3857, clone=True)
        pnt1 = fromstr(
            to_point, srid=4326
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
        raise ValueError('Error al consultar precio del servicio')
    except Exception as ex:
        print(ex)
        raise ValueError('Error al consultar precio del servicio')
