# Rest framework
from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
# Serializers
from scooter.apps.orders.serializers import DetailOrderSerializer
# Models
from scooter.apps.orders.models.orders import (OrderDetail)
from scooter.apps.stations.models import Station, StationService, MemberStation
from scooter.apps.common.models import Service, OrderStatus, Notification
from scooter.apps.customers.models import CustomerAddress
from scooter.apps.orders.models.orders import Order
# Functions channels
from scooter.apps.orders.utils.orders import send_order_to_station_channel
from asgiref.sync import async_to_sync
# Serializers primary field
from scooter.apps.common.serializers.common import CustomerFilteredPrimaryKeyRelatedField
# Task Celery
from scooter.apps.taskapp.tasks import send_notification_push_task
# Methods helpers
from scooter.apps.orders.serializers.orders import (calculate_service_price,
                                                    get_nearest_delivery_man)
# Utilities
import random
from string import ascii_uppercase, digits


class CreateOrderSerializer(serializers.Serializer):
    """ Create new order for customer"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
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
            exist_service = station.services.get(service=data['service'])
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
            data_service = calculate_service_price(from_address=data['from_address'],
                                                   to_address=data['to_address'],
                                                   service=data['station_service'])

            maximum_response_time = timezone.localtime(timezone.now()) + timedelta(minutes=2)
            qr_code = generate_qr_code()
            order_status = OrderStatus.objects.get(slug_name="without_delivery")
            order = Order.objects.create(**data,
                                         qr_code=qr_code,
                                         service_price=data_service['price_service'],
                                         distance=data_service['distance'],
                                         maximum_response_time=maximum_response_time,
                                         order_status=order_status)

            # Save detail order
            details_to_save = [OrderDetail(**detail, order=order) for detail in details]
            OrderDetail.objects.bulk_create(details_to_save)

            # Check if the station has manual assignment activated
            station = data['station']
            # Is assign delivery manually is true, then send notification
            if station.assign_delivery_manually:
                send_notification_push_task.delay(station.user.id,
                                                  'Solicitud nueva',
                                                  'Ha recibido una nueva solicitud',
                                                  {"type": "NEW_ORDER",
                                                   "order_id": order.id,
                                                   "message": "Ha recibido una nueva solicitud",
                                                   'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                   })
                Notification.objects.create(user_id=station.user_id, title="Solicitud nueva",
                                            type_notification_id=1,
                                            body="Has recibido una solicitud nueva")
                # Send message by django channel
                async_to_sync(send_order_to_station_channel)(station.id, order.id)
            else:
                # Get nearest delivery man
                delivery_man = get_nearest_delivery_man(from_location=data['from_address'], station=data['station'],
                                                        list_exclude=[], distance=5)
                # Send push notification to delivery_man
                if not delivery_man:
                    raise ValueError('No se encuentran repartidores disponibles')

                user_id = delivery_man.user_id

                send_notification_push_task.delay(user_id,
                                                  'Solicitud nueva',
                                                  'Pedido de nuevo',
                                                  {"type": "NEW_ORDER",
                                                   "order_id": order.id,
                                                   "message": "Pedido de nuevo",
                                                   'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                   })
                Notification.objects.create(user_id=user_id, title="Nueva solicitud",
                                            type_notification_id=1,
                                            body="Has recibido una nueva solicitud")

            # Add client to station or update info
            member, created = MemberStation.objects.get_or_create(customer=data['customer'],
                                                                  station=station)

            if created:
                Notification.objects.create(user_id=station.user_id, title="Nuevo cliente",
                                            type_notification_id=1,
                                            body="Se ha agregado un nuevo cliente")
            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al crear la orden'})


def generate_qr_code():
    try:
        CODE_LENGTH = 6
        """ Handle code creation """
        pool = ascii_uppercase + digits
        code = ''.join(random.choices(pool, k=CODE_LENGTH))
        while Order.objects.filter(qr_code=code).exists():
            code = ''.join(random.choices(pool, k=CODE_LENGTH))

        return code
    except Exception as ex:
        raise ValueError('Error al generar el codigo qr')
