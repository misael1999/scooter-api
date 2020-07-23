# Rest framework
from datetime import timedelta

from django.conf import settings
from django.db.models import Avg
from django.utils import timezone
from rest_framework import serializers
# Serializers
from scooter.apps.orders.models.ratings import RatingOrder
from scooter.apps.orders.serializers import DetailOrderSerializer
# Models
from scooter.apps.orders.models.orders import (OrderDetail, HistoryRejectedOrders)
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
    details = DetailOrderSerializer(many=True, required=False, allow_null=True)
    station_id = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(), source="station")
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="service")
    from_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects, source="from_address")
    to_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects, source="to_address")
    indications = serializers.CharField(max_length=500, required=False)
    approximate_price_order = serializers.CharField(max_length=30)
    phone_number = serializers.CharField(max_length=15)
    validate_qr = serializers.BooleanField(default=False, allow_null=True)

    def validate(self, data):
        try:
            # Add customer of the context in object data
            data['customer'] = self.context['customer']
            now = timezone.localtime(timezone.now())
            offset = now - timedelta(minutes=4)
            # Total de ordenes que se hicieron en ese rango de tiempo
            total_orders_range = Order.objects.filter(order_date__gte=offset, order_date__lt=now).count()

            if total_orders_range >= settings.ORDER_PER_CUSTOMER:
                raise serializers.ValidationError({'detail': 'Solo puedes hacer {} pedidos'
                                                             ' a la vez, espera que termine uno'
                                                  .format(settings.ORDER_PER_CUSTOMER)}, code="limit_orders")

            total_orders_in_process = Order.objects.filter(in_process=True, customer=data['customer']).count()
            # Validate that the orders in process are not greater than those allowed
            if total_orders_in_process >= settings.ORDER_PER_CUSTOMER \
                    or (total_orders_range + total_orders_in_process) == settings.ORDER_PER_CUSTOMER:
                raise serializers.ValidationError({'detail': 'Solo puedes hacer {} pedidos'
                                                             ' a la vez, espera que termine uno'
                                                  .format(settings.ORDER_PER_CUSTOMER)}, code="limit_orders")

            station = data['station']
            exist_service = station.services.get(service=data['service'])
            # if not exist_service:
            #     raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})
            data['station_service'] = exist_service
        except StationService.DoesNotExist:
            raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})
        return data

    def create(self, data):
        """ Create a new order and send message socket """
        try:
            details = data.pop('details', None)

            # Check if the station has manual assignment activated
            station = data['station']
            # Calculate price between two address
            data_service = calculate_service_price(from_address=data['from_address'],
                                                   to_address=data['to_address'],
                                                   service=data['station_service'])

            maximum_response_time = timezone.localtime(timezone.now()) + timedelta(minutes=2)
            qr_code = generate_qr_code()
            order_status = OrderStatus.objects.get(slug_name="without_delivery")

            # Add client to station or update info
            member, created = MemberStation.objects.get_or_create(customer=data['customer'],
                                                                  station=station)

            if created:
                Notification.objects.create(user_id=station.user_id, title="Nuevo cliente",
                                            type_notification_id=1,
                                            body="Se ha agregado un nuevo cliente")

            order = Order.objects.create(**data,
                                         member_station=member,
                                         qr_code=qr_code,
                                         order_date=timezone.localtime(timezone.now()),
                                         service_price=data_service['price_service'],
                                         distance=data_service['distance'],
                                         maximum_response_time=maximum_response_time,
                                         order_status=order_status)

            # Save detail order
            if details is not None:
                details_to_save = [OrderDetail(**detail, order=order) for detail in details]
                OrderDetail.objects.bulk_create(details_to_save)

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
                # Notification.objects.create(user_id=station.user_id, title="Solicitud nueva",
                #                             type_notification_id=1,
                #                             body="Has recibido una solicitud nueva")
                # Send message by django channel
                async_to_sync(send_order_to_station_channel)(station.id, order.id)
            else:
                location_selected = None
                if order.order_status.slug_name == "pick_up":
                    location_selected = order.from_address
                else:
                    location_selected = order.to_address

                # Get nearest delivery man
                delivery_man = get_nearest_delivery_man(location_selected=location_selected, station=data['station'],
                                                        list_exclude=[], distance=6)
                # Send push notification to delivery_man
                if not delivery_man:
                    raise ValueError('No se encuentran repartidores disponibles')

                user_id = delivery_man.user_id
                # Save delivery man in history rejected for not find again
                HistoryRejectedOrders.objects.get_or_create(delivery_man=delivery_man, order=order)

                send_notification_push_task.delay(user_id,
                                                  'Solicitud nueva',
                                                  'Pedido de nuevo',
                                                  {"type": "NEW_ORDER",
                                                   "order_id": order.id,
                                                   "message": "Pedido de nuevo",
                                                   'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                   })
                # Notification.objects.create(user_id=user_id, title="Nueva solicitud",
                #                             type_notification_id=1,
                #                             body="Has recibido una nueva solicitud")

            return order.id
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al crear la orden'})


class RetryOrderSerializer(serializers.Serializer):

    station_id = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(), source="station")

    def update(self, order, data):
        try:
            order.station = data['station']
            order.save()

            location_selected = None

            if order.order_status.slug_name == "pick_up":
                location_selected = order.from_address
            else:
                location_selected = order.to_address

            # Get list that excludes delivery men that are in the history of rejected orders
            list_exclude = HistoryRejectedOrders.objects.filter(
                order=order
            ).values_list('delivery_man_id', flat=True)

            delivery_man = get_nearest_delivery_man(location_selected=location_selected, station=data['station'],
                                                    list_exclude=list_exclude, distance=6)

            if not delivery_man:
                raise ValueError('No se encuentran repartidores disponibles, intente con otra central')

            send_notification_push_task.delay(delivery_man.user_id,
                                              'Solicitud nueva',
                                              'Ha recibido una nueva solicitud',
                                              {"type": "NEW_ORDER", "order_id": order.id,
                                               "message": "Ha recibido una nueva solicitud",
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                               })

            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in rating order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al calificar la orden'})


class RantingOrderCustomerSerializer(serializers.Serializer):
    """ Rated order by customer """
    rating = serializers.FloatField(min_value=1, max_value=5)
    comments = serializers.CharField(required=False)

    def validate(self, data):

        order = self.context['order']
        customer = self.context['customer']

        rating_exist = RatingOrder.objects.filter(order=order, rating_customer=customer).exists()

        if rating_exist:
            raise serializers.ValidationError({'detail': 'Ya se califico esta orden'})

        if order.in_process is True or order.date_delivered_order is None:
            raise serializers.ValidationError({'detail': 'No es permitido valorar esta orden'})

        data['rating_customer'] = customer
        data['user'] = customer.user
        data['station'] = order.station
        data['delivery_man'] = order.delivery_man
        data['order'] = order
        return data

    def create(self, data):
        try:
            station = data['station']
            delivery_man = data['delivery_man']
            # Create new rating order
            rating_order = RatingOrder.objects.create(
               **data
            )

            # Update reputation station
            station_avg = round(
                RatingOrder.objects.filter(
                    station=data['station'],
                ).aggregate(Avg('rating'))['rating__avg'],
                1
            )
            station.reputation = station_avg
            station.save()

            # Update reputation delivery man
            delivery_man_avg = round(
                RatingOrder.objects.filter(
                    delivery_man=delivery_man,
                    station=data['station']
                ).aggregate(Avg('rating'))['rating__avg'],
                1
            )

            delivery_man.reputation = delivery_man_avg
            delivery_man.save()

            Notification.objects.create(user_id=station.user_id, title="Ha recibido una nueva valoración",
                                        type_notification_id=1)


            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in rating order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al calificar la orden'})


def generate_qr_code():
    try:
        CODE_LENGTH = 8
        """ Handle code creation """
        pool = ascii_uppercase + digits
        code = ''.join(random.choices(pool, k=CODE_LENGTH))
        while Order.objects.filter(qr_code=code).exists():
            code = ''.join(random.choices(pool, k=CODE_LENGTH))

        return code
    except Exception as ex:
        raise ValueError('Error al generar el codigo qr')
