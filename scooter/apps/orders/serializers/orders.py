# Rest framework
from asgiref.sync import async_to_sync
from django.contrib.gis.geos import fromstr
from rest_framework import serializers
# Serializers
from scooter.apps.common.serializers.common import Base64ImageField
# Models
from scooter.apps.orders.models.orders import (Order, OrderDetail)
from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.stations.models import Station, StationService
from scooter.apps.common.models import Service
from scooter.apps.customers.models import CustomerAddress
from scooter.apps.orders.models.orders import Order
# Functions channels
from scooter.apps.orders.utils.orders import send_order
from asgiref.sync import async_to_sync
# Django Geo
from django.contrib.gis.measure import D
# FCM
from fcm_django.models import FCMDevice
# Serializers primary field
from scooter.apps.common.serializers.common import CustomerFilteredPrimaryKeyRelatedField
# GeoPy


# For requests we must put all the fields as read only
class OrderModelSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(source='created')

    class Meta:
        model = Order
        fields = ("delivery_man", "station", "service",
                  "from_address_id", "to_address_id", "service_price",
                  "indications", "approximate_price_order",
                  "date_delivered_order", "qr_code", "order_status", "order_date")


class DetailOrderSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=60)
    picture = Base64ImageField(required=False)


class RejectOrderByDelivery(serializers.Serializer):
    """ Reject order by delivery man and find another delivery man """
    order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), source='order')

    def validate(self, data):
        return data

    def create(self, data):
        return data


class CalculateServicePriceSerializer(serializers.Serializer):
    """ Calculate the price of the service before requesting the service """
    from_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects.all(),
                                                             source="from_address")
    to_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects.all(), source="to_address")
    station_id = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(), source="station")
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="service")

    def validate(self, data):
        # Check if the station has the requested service
        try:
            station = data['station']
            exist_service = station.stationservice_set.get(service=data['service'])
            # if not exist_service:
            #     raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})
            data['station_service'] = exist_service
        except StationService.DoesNotExist:
            raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})

        return data

    def create(self, data):
        try:
            price_service = calculate_service_price(data)
            return price_service
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al consultar precio de la orden'})


class CreateOrderSerializer(serializers.Serializer):
    """ Create new order for customer"""
    details = DetailOrderSerializer(many=True)
    station_id = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(), source="station")
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="service")
    from_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects, source="from_address")
    to_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects, source="to_address")
    service_price = serializers.FloatField()
    indications = serializers.CharField(max_length=300, required=False)
    approximate_price_order = serializers.FloatField()

    def validate(self, data):

        try:
            station = data['station']
            exist_service = station.stationservice_set.get(service=data['service'])
            # if not exist_service:
            #     raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})
            data['station_service'] = exist_service
        except StationService.DoesNotExist:
            raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})

        # Add customer of the context in object data
        data['customer'] = self.context['customer']
        return data

    def create(self, data):
        """ Create a new order and send message socket """
        try:
            details = data.pop('details', None)
            # Calculate price between two address
            price_service = calculate_service_price(data)
            order = Order.objects.create(**data, price_service=price_service)

            # Save detail order
            details_to_save = [OrderDetail(**detail, order=order) for detail in details]
            OrderDetail.objects.bulk_create(details_to_save)

            # Check if the station has manual assignment activated
            station = data['station']
            if station.assign_delivery_manually:
                send_notification_push(station.user, 'Prueba central', 'Esta es una prueba', {"test": "test"})
                # Send message by django channel
                # async_to_sync(send_order)(station.user, order)
            else:
                # Get nearest delivery man
                delivery_man = get_nearest_delivery_man(data['from_address'], data['station'])
                # Send push notification to delivery_man
                if not delivery_man:
                    raise ValueError('No se encuentran repartidores disponibles')
                send_notification_push(delivery_man.user, 'Prueba', 'Esta es una prueba', {"test": "test"})
            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al crear la orden'})


# Methods helpers
def get_nearest_delivery_man(from_location, station):
    """ assign the number of attempts to find a delivery man """

    # List of delivery men nearest
    delivery_men = DeliveryMan.objects \
        .filter(station=station, location__distance_lte=(from_location.point, D(km=10))).last()
    return delivery_men


def send_notification_push(user, title, body, data):
    devices = FCMDevice.objects.filter(user=user)
    if devices:
        devices.send_message(title=title, body=body, data=data)


def calculate_service_price(data):
    try:
        from_address = data['from_address']
        to_address = data['to_address']
        # longitude position 0 and latitude position 1
        # from_point = (from_address.point[1], from_address.point[0])
        # to_point = (to_address.point[1], to_address.point[0])
        pnt = fromstr(
            from_address.point, srid=4326
        ).transform(900913, clone=True)
        pnt1 = fromstr(
            to_address.point, srid=4326
        ).transform(900913, clone=True)
        distance_points = (pnt.distance(pnt1) / 1000) + 1
        service = data['station_service']
        price_service = 0.0
        if distance_points <= service.to_kilometer:
            price_service = service.base_rate_price
        else:
            kilometers_left = distance_points - service.to_kilometer
            price_service = service.base_rate_price + (kilometers_left * service.price_kilometer)

        return price_service
    except ValueError as e:
        raise ValueError('Error al consultar precio de la orden')
    except Exception as ex:
        raise ValueError('Error al consultar precio de la orden')
