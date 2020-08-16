# Rest framework
from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models import Avg
from django.utils import timezone
from rest_framework import serializers
# Serializers
from scooter.apps.customers.serializers import PointSerializer
from scooter.apps.merchants.models import Merchant
from scooter.apps.orders.models.ratings import RatingOrder
from scooter.apps.orders.serializers import DetailOrderSerializer
# Models
from scooter.apps.orders.models.orders import (OrderDetail, HistoryRejectedOrders)
from scooter.apps.stations.models import Station, StationService, MemberStation
from scooter.apps.common.models import Service, OrderStatus, Notification
from scooter.apps.customers.models import CustomerAddress
from scooter.apps.orders.models.orders import Order
# Functions channels
from scooter.apps.orders.utils.orders import notify_merchants, notify_delivery_men
from asgiref.sync import async_to_sync
# Serializers primary field
from scooter.apps.common.serializers.common import CustomerFilteredPrimaryKeyRelatedField
# Task Celery
from scooter.apps.taskapp.tasks import send_notification_push_task
# Methods helpers
from scooter.apps.orders.serializers.orders import (calculate_service_price,
                                                    get_nearest_delivery_man, is_free_order)
# Utilities
import random
from string import ascii_uppercase, digits

from scooter.utils.functions import send_notification_push_order


class CurrentLocationAddressSerializer(serializers.ModelSerializer):
    point = PointSerializer()

    class Meta:
        model = CustomerAddress
        fields = ("alias", "full_address",
                  "references", "point")


class CreateOrderSerializer(serializers.Serializer):
    """ Create new order for customer"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    details = DetailOrderSerializer(many=True, required=False, allow_null=True)
    station_id = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(),
                                                    source="station", required=False, allow_null=True)
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="service")
    # Modified to add address recommendations
    current_location = CurrentLocationAddressSerializer(required=False, allow_null=True,
                                                        help_text="For selected current location fast delivered")
    is_current_location = serializers.BooleanField(required=False, allow_null=True)
    from_address_id = serializers.PrimaryKeyRelatedField(queryset=CustomerAddress.objects.all(), source="from_address")
    to_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects, source="to_address",
                                                           required=False, allow_null=True)

    indications = serializers.CharField(max_length=500, required=False)
    approximate_price_order = serializers.CharField(max_length=30)
    phone_number = serializers.CharField(max_length=15)
    validate_qr = serializers.BooleanField(default=False, allow_null=True)
    # Merchants
    merchant_id = serializers.PrimaryKeyRelatedField(queryset=Merchant.objects.all(), source="merchant",
                                                     required=False, allow_null=True)
    is_order_to_merchant = serializers.BooleanField(required=True, allow_null=True)

    def validate(self, data):
        try:
            # Add customer of the context in object data
            # now = timezone.localtime(timezone.now())
            # offset = now - timedelta(minutes=4)
            # # Total de ordenes que se hicieron en ese rango de tiempo
            # total_orders_range = Order.objects.filter(order_date__gte=offset, order_date__lt=now).count()
            #
            # if total_orders_range >= settings.ORDER_PER_CUSTOMER:
            #     raise serializers.ValidationError({'detail': 'Solo puedes hacer {} pedidos'
            #                                                  ' a la vez, espera que termine uno'
            #                                       .format(settings.ORDER_PER_CUSTOMER)}, code="limit_orders")
            #
            # total_orders_in_process = Order.objects.filter(in_process=True, customer=data['customer']).count()
            # # Validate that the orders in process are not greater than those allowed
            # if total_orders_in_process >= settings.ORDER_PER_CUSTOMER \
            #         or (total_orders_range + total_orders_in_process) == settings.ORDER_PER_CUSTOMER:
            #     raise serializers.ValidationError({'detail': 'Solo puedes hacer {} pedidos'
            #                                                  ' a la vez, espera que termine uno'
            #                                       .format(settings.ORDER_PER_CUSTOMER)}, code="limit_orders")

            station = data['station']
            data['customer'] = self.context['customer']
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
            customer = data['customer']
            station = data.get('station', None)
            merchant = data.get('merchant', None)

            maximum_response_time = timezone.localtime(timezone.now()) + timedelta(minutes=settings.TIME_RESPONSE)
            is_safe_order = customer.is_safe_user

            # if station.assign_delivery_manually:
            #     order_status = OrderStatus.objects.get(slug_name="without_delivery")

            is_current_location = data.pop('is_current_location', False)
            to_address = data.pop('current_location', None)

            if is_current_location:
                if to_address:
                    point = Point(x=to_address['point']['lng'], y=to_address['point']['lat'], srid=4326)
                    to_address['point'] = point
                    customer_address = CustomerAddress.objects.create(**to_address,
                                                                      customer=customer,
                                                                      exterior_number='',
                                                                      type_address_id=1,
                                                                      status_id=1)

                    data['to_address'] = customer_address

            # Calculate price order ==========
            # Calculate price between two address

            data_service = calculate_service_price(from_address=data['from_address'].point,
                                                   to_address=data['to_address'].point,
                                                   service=data['station_service'],
                                                   is_current_location=False,
                                                   point=None
                                                   )
            price = 0.0

            if not is_free_order(station):
                price = data_service['price_service']

            is_order_to_merchant = data.get('is_order_to_merchant', False)
            if is_order_to_merchant:
                if not self.valid_stock(details):
                    raise ValueError('Un producto no cuenta con suficiente stock')
                order_status = OrderStatus.objects.get(slug_name="await_confirmation_merchant")
                data['order_price'] = self.calculate_order_price(details)
                data['merchant_location'] = merchant.point
                data['total_order'] = data['order_price'] + price

            else:
                order_status = OrderStatus.objects.get(slug_name="await_delivery_man")

            data['order_status'] = order_status
            data['qr_code'] = generate_qr_code()
            data['price'] = price
            data['distance'] = data_service['distance']
            data['is_safe_order'] = is_safe_order
            data['order_date'] = timezone.localtime(timezone.now())
            data['maximum_response_time'] = maximum_response_time
            order = Order.objects.create(**data)

            # Save detail order
            details_to_save = []
            if details and is_order_to_merchant:
                details_to_save = self.update_stock(details)
            elif details:
                details_to_save = [OrderDetail(**detail, order=order) for detail in details]

            OrderDetail.objects.bulk_create(details_to_save)
            # Is assign delivery manually is true, then send notification
            # if station.assign_delivery_manually:
            #     send_notification_push_task.delay(station.user_id,
            #                                       'Solicitud nueva',
            #                                       'Ha recibido una nueva solicitud',
            #                                       {"type": "NEW_ORDER",
            #                                        "order_id": order.id,
            #                                        "message": "Ha recibido una nueva solicitud",
            #                                        'click_action': 'FLUTTER_NOTIFICATION_CLICK'
            #                                        })
            #     # Send message by django channel
            #     async_to_sync(send_order_to_station_channel)(station.id, order.id)
            # else:
            location_selected = None
            location_selected = get_ref_location(order)

            if is_order_to_merchant:
                async_to_sync(notify_merchants)(merchant.id, order.id)
            else:
                send_order_delivery(location_selected=location_selected,
                                    station=station,
                                    order=order)
            # Get nearest delivery

            # user_id = delivery_man.user_id
            # Save delivery man in history rejected for not find again
            # HistoryRejectedOrders.objects.get_or_create(delivery_man=delivery_man, order=order)

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

    def create_order(self, data):
        pass

    def valid_stock(self, details):
        is_valid = True

        for detail in details:
            product = detail['product']
            if product.stock < detail['quantity']:
                is_valid = False
                break

        return is_valid

    def calculate_order_price(self, details):
        price_order = 0.0
        for detail in details:
            price_order = price_order + (detail['product'].price * detail['quantity'])

        return price_order

    def update_stock(self, details, order):
        details_to_save = []
        for detail in details:
            product = detail['product']
            product.stock = product.stock - detail['quantity']
            product.save()
            detail_product = OrderDetail(**detail,
                                         product_price=product.price,
                                         order=order)
            details_to_save.append(detail_product)

        return details_to_save


class RetryOrderSerializer(serializers.Serializer):
    station_id = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(), source="station")

    def update(self, order, data):
        try:
            order.station = data['station']
            order.maximum_response_time = timezone.localtime(timezone.now()) + timedelta(minutes=settings.TIME_RESPONSE)
            order.order_status = OrderStatus.objects.get(slug_name="await_delivery_man")
            order.save()
            location_selected = None

            if order.order_status.slug_name == "pick_up":
                location_selected = order.from_address
            else:
                location_selected = get_ref_location(order)

            # Get list that excludes delivery men that are in the history of rejected orders
            list_exclude = HistoryRejectedOrders.objects.filter(
                order=order
            ).values_list('delivery_man_id', flat=True)

            # Get nearest delivery man
            send_order_delivery(location_selected=location_selected, station=data['station'],
                                order=order)

            return order.id
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


def send_order_delivery(location_selected, station, order):
    try:
        # Get nearest delivery man
        delivery_men = get_nearest_delivery_man(location_selected=location_selected, station=station,
                                                list_exclude=[], distance=settings.RANGE_DISTANCE,
                                                status=['available', 'busy', 'out_service'])

        # Send push notification to delivery_man
        if delivery_men.count() == 0:
            delivery_men = get_nearest_delivery_man(location_selected=location_selected, station=station,
                                                    list_exclude=[], distance=settings.RANGE_DISTANCE,
                                                    status=['available', 'busy'])

            if delivery_men.count() == 0:
                delivery_men = get_nearest_delivery_man(location_selected=location_selected, station=station,
                                                        list_exclude=[], distance=settings.RANGE_DISTANCE,
                                                        status=['available', 'busy', 'out_service'])
                if delivery_men.count() == 0:
                    raise ValueError('No se encontraron repartidores disponibles')

        for delivery_man in delivery_men:
            user_id = delivery_man.user_id
            send_notification_push_order(user_id=user_id,
                                         title='Solicitud nueva',
                                         body='Ha recibido un nuevo pedido',
                                         sound="ringtone.mp3",
                                         android_channel_id="alarms",
                                         data={"type": "NEW_ORDER",
                                               "order_id": order.id,
                                               "ordering": "",
                                               "message": "Pedido de nuevo",
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                               })
        async_to_sync(notify_delivery_men)(order.id, 'NEW_ORDER')

    except ValueError as e:
        raise ValueError(e)
    except Exception as ex:
        raise ValueError('Error al mandar notificaciones')


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


# Check if the order is safe and get location
def get_ref_location(order):
    if order.order_status.slug_name == "pick_up":
        location_selected = order.from_address
    else:
        # If safe order, then find delivery man nearest from purchase place
        if order.is_safe_order:
            location_selected = order.from_address
        else:
            location_selected = order.to_address
    return location_selected
