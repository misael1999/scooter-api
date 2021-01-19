# Rest framework
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
# Serializers
from scooter.apps.customers.serializers import PointSerializer
from scooter.apps.merchants.models import Merchant
from scooter.apps.orders.serializers.v2 import generate_qr_code, valid_promotion, get_ref_location, send_order_delivery
from scooter.apps.orders.serializers.v2.orders import DetailOrderSerializer
# Models
from scooter.apps.orders.models.orders import (OrderDetail, OrderDetailMenu,
                                               OrderDetailMenuOption)
from scooter.apps.payments.models import Card
from scooter.apps.stations.models import Station, StationService
from scooter.apps.common.models import Service, OrderStatus
from scooter.apps.customers.models import CustomerAddress
from scooter.apps.orders.models.orders import Order
# Functions channels
# Serializers primary field
from scooter.apps.common.serializers.common import CustomerFilteredPrimaryKeyRelatedField
# Task Celery
from scooter.apps.taskapp.tasks import send_notification_push_task
# Methods helpers
from scooter.apps.orders.serializers.orders import (calculate_service_price, is_free_order)
# Utilities
import random
from scooter.utils.functions import (send_notification_push_order_with_sound,)
# Conekta
import conekta

conekta.api_key = settings.CONEKTA_API_KEY
conekta.api_version = settings.CONEKTA_API_VERSION


class CurrentLocationAddressSerializer(serializers.ModelSerializer):
    point = PointSerializer()

    class Meta:
        model = CustomerAddress
        fields = ("alias", "full_address",
                  "references", "point")


class CreateOrderV3Serializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    details = DetailOrderSerializer(many=True, required=False, allow_null=True)
    station_id = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all(),
                                                    source="station", required=False, allow_null=True)
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="service")

    # Modified to add address recommendations
    from_address_id = serializers.PrimaryKeyRelatedField(allow_null=True, allow_empty=True, required=False,
                                                         queryset=CustomerAddress.objects.all(),
                                                         source="from_address")
    to_address_id = CustomerFilteredPrimaryKeyRelatedField(queryset=CustomerAddress.objects, source="to_address",
                                                           required=False, allow_null=True)

    validate_qr = serializers.BooleanField(default=False, allow_null=True)

    # Merchants
    merchant_id = serializers.PrimaryKeyRelatedField(allow_null=True, allow_empty=True, required=False,
                                                     queryset=Merchant.objects.all(), source="merchant")
    is_order_to_merchant = serializers.BooleanField(required=True, allow_null=True)

    # Payment methods
    payment_method = serializers.IntegerField(default=1, required=False, allow_null=True)
    card_id = CustomerFilteredPrimaryKeyRelatedField(required=False, queryset=Card.objects,
                                                     source="card", allow_null=True,
                                                     allow_empty=True)

    class Meta:
        model = Order
        fields = ('user', 'details', 'station_id', 'service_id', 'from_address_id', 'to_address_id',
                  'indications', 'approximate_price_order', 'phone_number', 'validate_qr', 'merchant_id',
                  'is_order_to_merchant', 'promotion', 'payment_method', 'card_id')

    def validate(self, data):
        try:
            station = data.get('station', None)
            merchant = data.get('merchant', None)
            if merchant and merchant.is_delivery_by_store is False and not station:
                raise serializers.ValidationError({'detail': 'Selecciona una central'})
            if station is not None:
                exist_service = station.services.get(service=data['service'])
                data['station_service'] = exist_service

            data['customer'] = self.context['customer']
            # if not exist_service:
            #     raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})
        except StationService.DoesNotExist:
            raise serializers.ValidationError({'detail': 'La central no cuenta con el servicio solicitado'})
        return data

    def create(self, data):
        """ Create a new order and send message socket """
        try:
            details = data.pop('details', None)
            card = data.pop('card', None)
            station = data.get('station', None)
            merchant = data.get('merchant', None)
            customer_promotion = data.get('promotion', None)
            price_promotion = None
            maximum_response_time = timezone.localtime(timezone.now()) + timedelta(minutes=settings.TIME_RESPONSE)
            if customer_promotion:
                price_promotion = valid_promotion(customer_promotion)
                customer_promotion.used = True
                customer_promotion.save()

            is_safe_order = True

            is_order_to_merchant = data.get('is_order_to_merchant', False)

            price = 0.0
            from_address = None
            if is_order_to_merchant:
                from_address = merchant.point
            else:
                from_address = data['from_address'].point

            if station and not is_free_order(station):
                data_service = calculate_service_price(from_address=from_address,
                                                       to_address=data['to_address'].point,
                                                       service=data['station_service'],
                                                       is_current_location=False,
                                                       point=None
                                                       )
                price = data_service['price_service']
                data['distance'] = data_service['distance']

            if is_order_to_merchant:
                data['in_process'] = True
                if merchant.is_open:
                    # if not self.valid_stock(details):
                    #     raise ValueError('Un producto no cuenta con suficiente stock')
                    order_status = OrderStatus.objects.get(slug_name="await_confirmation_merchant")
                    data['merchant_location'] = merchant.point
                    data['is_delivery_by_store'] = merchant.is_delivery_by_store
                    if merchant.is_delivery_by_store:
                        data.pop('station', None)
                else:
                    raise ValueError('{} ha cerrado'.format(merchant.merchant_name))
            else:
                order_status = OrderStatus.objects.get(slug_name="await_delivery_man")

            data['order_status'] = order_status
            data['qr_code'] = generate_qr_code()
            if price_promotion is not None:
                data['service_price'] = price_promotion['price']
            else:
                data['service_price'] = price
            data['is_safe_order'] = is_safe_order
            data['order_date'] = timezone.localtime(timezone.now())
            data['maximum_response_time'] = maximum_response_time
            data['date_update_order'] = timezone.localtime(timezone.now())
            order = Order.objects.create(**data)
            details_to_conekta = []

            # Save detail order
            if details and is_order_to_merchant:
                resp = self.create_details_merchant(details=details, order=order,
                                                    increment_price=merchant.increment_price_operating,
                                                    has_rate_operating=merchant.has_rate_operating)
                details_to_conekta = resp['details_to_conekta']
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
            if is_order_to_merchant:
                # Verificar si el pago es con tarjeta:
                payment_method = data.get('payment_method', 1)
                if payment_method == 2:
                    # Realizamos el cobro con tarjeta
                    if not card:
                        raise ValueError('No has ingresado una tarjeta valida')
                    # Crear orden de conekta
                    order_conekta = self.create_order_conekta(card=card, order=order, items=details_to_conekta)
                    order.is_payment_online = True
                    order.order_conekta_id = order_conekta.id
                    order.card = card
                    order.save()

                # async_to_sync(notify_merchants)(merchant.id, order.id, 'NEW_ORDER')
                # async_to_sync(send_order_to_station_channel)(station.id, order.id)
                send_notification_push_order_with_sound(user_id=merchant.user_id,
                                                        title='Pedido entrante',
                                                        body='Ha recibido un nuevo pedido',
                                                        sound="ringtone.mp3",
                                                        android_channel_id="alarms",
                                                        data={"type": "NEW_ORDER",
                                                              "order_id": order.id,
                                                              "message": "Pedido de nuevo",
                                                              'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                              })
                send_notification_push_task.delay(user_id=station.user_id,
                                                  title='Pedido a comercio',
                                                  body='Un nuevo pedido en {}'.format(
                                                      merchant.merchant_name),
                                                  sound="preorder.mp3",
                                                  android_channel_id="preorder",
                                                  data={"type": "PREORDER",
                                                        "order_id": order.id,
                                                        "message": "Pedido de nuevo",
                                                        'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                        })
            else:
                location_selected = None
                location_selected = get_ref_location(order)
                if station.assign_delivery_manually:

                    send_notification_push_order_with_sound(user_id=station.user_id,
                                                            title='Pedido nuevo',
                                                            body='Solicitud nueva',
                                                            sound="alarms.mp3",
                                                            android_channel_id="alarms",
                                                            data={"type": "NEW_ORDER",
                                                                  "order_id": order.id,
                                                                  "message": "Pedido de nuevo",
                                                                  'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                                  })
                    # Send message by django channel
                    # async_to_sync(send_order_to_station_channel)(station.id, order.id)
                else:
                    # async_to_sync(send_order_to_station_channel)(station.id, order.id)
                    send_order_delivery(location_selected=location_selected.point,
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
            print("Exception in create order v2, please check it")
            print(ex.args.__str__())
            print(ex.__cause__)
            print(ex)
            raise serializers.ValidationError({'detail': 'Error al crear la orden'})

    def valid_stock(self, details):
        is_valid = True

        for detail in details:
            product = detail['product']
            if product.stock < detail['quantity']:
                is_valid = False
                break

        return is_valid

    def get_order_price(self, details):
        price_order = 0.0
        extra_price = 0.0
        menu_price = 0.0
        for detail in details:
            # Para sumar el precio de las opciones seleccionadas
            menu_options = detail.get('menu_options', [])
            for menu_option in menu_options:
                options = menu_option.get('options', [])
                menu_price = 0.0
                for option in options:
                    extra_price = extra_price + option['option'].price

            price_order = price_order + (detail['product'].price * detail['quantity'])

        return {
            'price_order': price_order,
            "extra_price": extra_price
        }

    def create_order_conekta(self, card, order, items):
        # Agregamos el precio del envío como item
        items.append(
            {
                "name": 'Servicio de moto',
                "unit_price": round(order.service_price * 100),
                "quantity": 1
            }
        )
        try:
            order_conekta = conekta.Order.create({
                "currency": "MXN",
                "pre_authorize": True,
                "customer_info": {
                    "customer_id": card.conekta_id
                },
                "line_items": items,
                "charges": [{
                    "payment_method": {
                        "type": "card",
                        "payment_source_id": card.source_id,
                    }
                }]

            })
            return order_conekta
        except conekta.ConektaError as e:
            print('Error un conekta, por favor revisar')
            print(e.details)
            print(e.code)
            print(e.debug_message)
            print(e.message)
            raise ValueError('Ah ocurrido un error al realizar el cobro')

    def create_details_merchant(self, details, order, has_rate_operating, increment_price):
        details_to_save = []
        details_to_conekta = []
        price_order = 0.0

        for detail in details:
            extra_price = 0.0
            menu_options = detail.pop('menu_options', [])
            product = detail['product']
            # product.stock = product.stock - detail['quantity']
            # product.save()
            # Save detail
            detail_product = OrderDetail.objects.create(**detail,
                                                        product_name=product.name,
                                                        product_price=product.price,
                                                        order=order)
            details_options_to_save = []
            # Obtener los menus(secciones) del producto
            for menu_option in menu_options:
                options = menu_option.pop('options', [])
                menu_price = 0.0
                detail_menu = OrderDetailMenu.objects.create(**menu_option,
                                                             detail=detail_product,
                                                             menu_name=menu_option['menu'].name)
                # Obtener las opciones seleccionadas del menu
                for option in options:
                    option_obj = option['option']
                    quantity = option.pop('quantity', 1)
                    # Acumular el precio extra que son las opciones que tienen un costo
                    extra_price = extra_price + (option_obj.price * quantity)
                    menu_price = menu_price + option_obj.price
                    details_options_to_save.append(OrderDetailMenuOption(**option,
                                                                         quantity=quantity,
                                                                         option_name=option_obj.name,
                                                                         price_option=option_obj.price,
                                                                         detail_menu=detail_menu))

                # El precio extra son las opciones que tienen un costo
                details_to_conekta.append({
                    "name": product.name,
                    "unit_price": round((product.price + extra_price) * 100),
                    "quantity": detail['quantity']
                })
                detail_menu.price = menu_price
                detail_menu.save()
            # El precio extra son las opciones que tienen un costo
            price_order = price_order + ((detail['product'].price + extra_price) * detail['quantity'])
            OrderDetailMenuOption.objects.bulk_create(details_options_to_save)

        order.order_price = price_order
        order.total_order = price_order + order.service_price + increment_price
        order.increment_price_operating = increment_price
        order.has_rate_operating = has_rate_operating
        order.save()

        return {'details_to_save': details_to_save, 'details_to_conekta': details_to_conekta}
