# Rest framework
from datetime import timedelta
from django.utils import timezone
from asgiref.sync import async_to_sync
from django.contrib.gis.geos import fromstr
from rest_framework import serializers
# Serializers
from scooter.apps.common.serializers.common import Base64ImageField
from scooter.apps.customers.serializers import CustomerAddressModelSerializer
# Models
from scooter.apps.orders.models.orders import (Order, OrderDetail)
from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.stations.models import Station, StationService
from scooter.apps.common.models import Service, DeliveryManStatus, OrderStatus
from scooter.apps.customers.models import CustomerAddress
from scooter.apps.orders.models.orders import Order, HistoryRejectedOrders
# Functions channels
from scooter.apps.orders.utils.orders import send_order_channel
from asgiref.sync import async_to_sync
# Django Geo
from django.contrib.gis.measure import D
# FCM
from fcm_django.models import FCMDevice
# Serializers primary field
from scooter.apps.common.serializers.common import CustomerFilteredPrimaryKeyRelatedField
# Task Celery
from scooter.apps.taskapp.tasks import send_notification_push_task

# GeoPy
# from geopy import distance


class DetailOrderSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=60)
    picture = Base64ImageField(required=False)


# For requests we must put all the fields as read only
class OrderModelSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(source='created')

    class Meta:
        model = Order
        fields = ("id", "delivery_man", "station", "station_service",
                  "from_address_id", "to_address_id", "service_price",
                  "indications", "approximate_price_order",
                  "date_delivered_order", "qr_code", "order_status", "order_date")


class OrderWithDetailModelSerializer(serializers.ModelSerializer):
    station = serializers.StringRelatedField(read_only=True)
    customer = serializers.StringRelatedField()
    order_date = serializers.DateTimeField(source='created')
    from_address = CustomerAddressModelSerializer()
    to_address = CustomerAddressModelSerializer()
    service = serializers.StringRelatedField(read_only=True, source="station_service")
    order_status = serializers.StringRelatedField(read_only=True)
    details = DetailOrderSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "customer","delivery_man", "station", "service",
                  "from_address", "to_address", "service_price",
                  "indications", "approximate_price_order",
                  "date_delivered_order", "qr_code", "order_status", "order_date",
                  'details')
        read_only_fields = fields


class AcceptOrderByDeliveryManSerializer(serializers.Serializer):

    def validate(self, data):
        order = self.context['order']
        delivery_man = self.context['delivery_man']
        # Verify that the order is from the same station as the delivery man
        if not order.station == delivery_man.station:
            raise serializers.ValidationError({'detail': 'El repartidor no se encuentra en la estación'},
                                              code='delivery_not_station')
        # Verify that the order does not have a delivery man assigned
        if order.delivery_man is not None:
            raise serializers.ValidationError({'detail': 'El pedido ya tiene un repartidor asignado'},
                                              code='order_already_delivery_man')
        data['order'] = order
        data['delivery_man'] = delivery_man
        return data

    def update(self, instance, data):
        try:
            delivery_man = data['delivery_man']
            order = data['order']
            # Update status delivery man
            delivery_status = DeliveryManStatus.objects.get(slug_name='busy')
            delivery_man.delivery_status = delivery_status
            delivery_man.save()
            # Update status order
            order_status = OrderStatus.objects.get(slug_name='process_money')
            order.order_status = order_status
            # Assign order to delivery man
            order.delivery_man = delivery_man
            order.save()
            # Send notification push to customer
            send_notification_push_task.delay(order.customer.user.id, 'Repartidor en camino',
                                              'Puedes ver el seguimiento de tu producto',
                                              {"type": "NEW_ORDER",
                                               "order_id": order.id})
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al aceptar el pedido'})


class RejectOrderByDeliverySerializer(serializers.Serializer):
    """ Reject order by delivery man and find another delivery man """
    # user = serializers.HiddenField(read_only=True, default=serializers.CurrentUserDefault())
    reason_rejection = serializers.CharField(max_length=70, required=False)

    def validate(self, data):
        order = self.context['order']
        delivery_man = self.context['delivery_man']
        # Verify that the order is from the same station as the delivery man
        if not order.station == delivery_man.station:
            raise serializers.ValidationError({'detail': 'El repartidor no se encuentra en la estación'},
                                              code='delivery_not_station')
        # Verify that the order does not have a delivery man assigned
        if order.delivery_man is not None:
            raise serializers.ValidationError({'detail': 'El pedido ya tiene un repartidor asignado'},
                                              code='order_already_delivery_man')
        return data

    def update(self, instance, data):
        try:
            delivery_man = self.context['delivery_man']
            # Save delivery man in history rejected orders for not find again and reported to station
            HistoryRejectedOrders.objects.get_or_create(delivery_man=delivery_man, order=instance)

            # Get list that excludes delivery men that are in the history of rejected orders
            list_exclude = HistoryRejectedOrders.objects.filter(
                order=instance
            ).values_list('delivery_man_id', flat=True)

            # Find the closest delivery man again, but exclude delivery men who are in the reject history
            delivery_man = get_nearest_delivery_man(from_location=instance.from_address, station=instance.station,
                                                    list_exclude=list_exclude, distance=6)
            if not delivery_man:
                raise ValueError('No se encuentran repartidores disponibles')

            send_notification_push_task.delay(delivery_man.user.id, 'Solicitud nueva',
                                              'Pedido de compra', {"type": "NEW_ORDER", "order_id": instance.id})
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al rechazar el pedido'})


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
            exist_service = station.stationservice_set.get(service=data['service'])
            # if not exist_service:
            #     raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})
            data['station_service'] = exist_service
            data.pop('service')
        except StationService.DoesNotExist:
            raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})

        return data

    def create(self, data):
        try:
            price_service = calculate_service_price(from_address=data['from_address'],
                                                    to_address=data['to_address'],
                                                    service=data['station_service'])
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
    indications = serializers.CharField(max_length=300, required=False)
    approximate_price_order = serializers.CharField(max_length=30)
    phone_number = serializers.CharField(max_length=15)

    def validate(self, data):

        try:
            station = data['station']
            exist_service = station.stationservice_set.get(service=data['service'])
            # if not exist_service:
            #     raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})
            data['station_service'] = exist_service
            data.pop('service')
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
            price_service = calculate_service_price(from_address=data['from_address'],
                                                    to_address=data['to_address'],
                                                    service=data['station_service'])

            maximum_response_time = timezone.localtime(timezone.now()) + timedelta(minutes=1.5)
            order = Order.objects.create(**data,
                                         service_price=price_service,
                                         maximum_response_time=maximum_response_time)

            # Save detail order
            details_to_save = [OrderDetail(**detail, order=order) for detail in details]
            OrderDetail.objects.bulk_create(details_to_save)

            # Check if the station has manual assignment activated
            station = data['station']
            # Is assign delivery manually is true, then send notification
            if station.assign_delivery_manually:
                send_notification_push_task.delay(station.user.id, 'Solicitud nueva',
                                                  'Ha recibido una nueva solicitud', {"type": "NEW_ORDER", "order_id": order.id})
                # Send message by django channel
                async_to_sync(send_order_channel)(station.user, order.id)
            else:
                # Get nearest delivery man
                delivery_man = get_nearest_delivery_man(from_location=data['from_address'], station=data['station'],
                                                        list_exclude=[], distance=5)
                # Send push notification to delivery_man
                if not delivery_man:
                    raise ValueError('No se encuentran repartidores disponibles')
                send_notification_push_task.delay(delivery_man.user.id, 'Solicitud nueva',
                                                  'Pedido de compra', {"type": "NEW_ORDER", "order_id": order.id})
            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al crear la orden'})


# Methods helpers
def get_nearest_delivery_man(from_location, station, list_exclude, distance):
    """ Get nearest delivery man and exclude who are in the history of rejected orders """

    # List of delivery men nearest
    delivery_man = DeliveryMan.objects.filter(station=station,
                                              location__distance_lte=(
                                                  from_location.point, D(km=distance))
                                              ).exclude(id__in=list_exclude).last()

    return delivery_man


def send_notification_push(user, title, body, data):
    devices = FCMDevice.objects.filter(user=user)
    if devices:
        devices.send_message(title=title, body=body, data=data)


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
        return price_service
    except ValueError as e:
        print(e)
        raise ValueError('Error al consultar precio de la orden')
    except Exception as ex:
        print(ex)
        raise ValueError('Error al consultar precio de la orden')
