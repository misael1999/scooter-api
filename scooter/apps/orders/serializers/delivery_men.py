# Rest framework
from datetime import timedelta

from rest_framework import serializers
from django.utils import timezone
# Serializers
# Models
from scooter.apps.common.models import DeliveryManStatus, OrderStatus, Notification, Service
from scooter.apps.customers.models import HistoryCustomerInvitation, CustomerPromotion
from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.orders.models.orders import HistoryRejectedOrders
# Functions channels
# Task Celery
from scooter.apps.taskapp.tasks import send_notification_push_task
# Functions
from scooter.apps.orders.serializers.orders import get_nearest_delivery_man
# Functions channels
from scooter.apps.orders.utils.orders import notify_station_accept
from scooter.apps.orders.utils.orders import notify_delivery_men
from asgiref.sync import async_to_sync

from scooter.utils.functions import send_notification_push_order, send_notification_push_order_with_sound


class AcceptOrderByDeliveryManSerializer(serializers.Serializer):

    def validate(self, data):
        order = self.context['order']
        delivery_man = self.context['delivery_man']

        if order.order_status.slug_name == 'rejected':
            raise serializers.ValidationError({'detail': 'El pedido fue rechazado, el tiempo de espera culmino'},
                                              code='order_already_delivery_man')

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
            if order.delivery_man == delivery_man:
                return data
            # Update status delivery man
            delivery_status = DeliveryManStatus.objects.get(slug_name='busy')
            delivery_man.delivery_status = delivery_status
            delivery_man.save()

            # Update status order
            if order.service.slug_name == 'pick_up':
                order_status = OrderStatus.objects.get(slug_name='pick_up')
                data_message = {
                    'title': "Repartidor en camino",
                    'body': "Tu scooter ya va en camino a recolectar tu pedido"
                }
            else:
                # Check if it is a safe order
                data_message = get_message_accept(order)
                order_status = OrderStatus.objects.get(slug_name=data_message['status_slug'])

            order.order_status = order_status
            # Assign order to delivery man
            order.delivery_man = delivery_man
            order.in_process = True
            order.save()
            # Send notification push to customer
            type_notification = "ACCEPTED_ORDER"
            if order.is_order_to_merchant:
                type_notification = "ACCEPT_ORDER_DELIVERY"
                send_notification_push_task.delay(instance.user_id,
                                                  data_message['title'],
                                                  data_message['body'],
                                                  {"type": type_notification,
                                                   "order_id": order.id,
                                                   "message": "Puedes ver el seguimiento de tu pedido",
                                                   'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                   })
                send_notification_push_task.delay(instance.merchant.user_id,
                                                  'El scooter ya va por el pedido',
                                                  'Numero de pedido {}'.format(order.qr_code),
                                                  {"type": type_notification,
                                                   "order_id": order.id,
                                                   "message": "Puedes ver el seguimiento de tu pedido",
                                                   'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                   })
            async_to_sync(notify_station_accept)(order.station_id, order.id)
            # Notify all delivery men that order was accepted
            async_to_sync(notify_delivery_men)(order.id, 'ORDER_ACCEPTED')

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
        # delivery_man = self.context['delivery_man']
        # Verify that the order does not have a delivery man assigned
        if order.delivery_man is not None:
            raise serializers.ValidationError({'detail': 'El pedido ya tiene un repartidor asignado'},
                                              code='order_already_delivery_man')
        return data

    def update(self, instance, data):
        try:
            raise ValueError('Metodo no implementado')

            delivery_man = self.context['delivery_man']
            # Save delivery man in history rejected orders for not find again and reported to station
            HistoryRejectedOrders.objects.get_or_create(delivery_man=delivery_man, order=instance)

            # Get list that excludes delivery men that are in the history of rejected orders
            list_exclude = HistoryRejectedOrders.objects.filter(
                order=instance
            ).values_list('delivery_man_id', flat=True)

            # Find the closest delivery man again, but exclude delivery men who are in the reject history
            delivery_man = get_nearest_delivery_man(location_selected=instance.to_address, station=instance.station,
                                                    list_exclude=list_exclude, distance=6)
            if not delivery_man:
                raise ValueError('No se encuentran repartidores disponibles')

            send_notification_push_task.delay(delivery_man.user_id,
                                              'Solicitud nueva',
                                              'Pedido de compra',
                                              {"type": "NEW_ORDER", "order_id": instance.id,
                                               "message": "Ha recibido una nueva solicitud",
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                               })
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al rechazar el pedido'})


class ScanQrOrderSerializer(serializers.Serializer):
    """ Scan qr to mark the order as delivered """

    qr_code = serializers.CharField(max_length=10)
    service = serializers.SlugRelatedField(slug_field="slug_name", queryset=Service.objects.all())

    def validate_qr_code(self, qr_code):
        order = self.context['order']
        if order.qr_code != qr_code:
            raise serializers.ValidationError({'detail': 'Código QR no valido para ese pedido'})
        return qr_code

    def update(self, instance, data):
        try:
            data_notification = {
                "title": 'Pedido entregado',
                "body": 'Tu pedido ha sido entregado',
                "type": "ORDER_DELIVERED"
            }
            # Update member station
            station = instance.station
            customer = instance.customer
            self.generate_free_delivery(customer=customer)

            instance = update_order_status(service=data['service'],
                                           order_status=OrderStatus.objects.get(slug_name="delivered"),
                                           instance=instance,
                                           data=data_notification
                                           )

            member_station = instance.member_station
            if member_station:
                member_station.total_orders = member_station.total_orders + 1
                member_station.save()
                if not customer.is_safe_user:
                    if station.quantity_safe_order >= member_station.total_orders:
                        customer.is_safe_user = True
                        customer.save()

            instance.date_delivered_order = timezone.localtime(timezone.now())
            instance.in_process = False
            instance.save()

            delivery_status = DeliveryManStatus.objects.get(slug_name="available")
            delivery_man = instance.delivery_man
            delivery_man.delivery_status = delivery_status
            delivery_man.save()

            # Notification.objects.create(user_id=instance.user_id, title="Califica tu pedido",
            #                             type_notification_id=1,
            #                             body="Tu pedido ha sido entregado, deja una calificación")
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al escanear el código'})

    def generate_free_delivery(self, customer):
        try:
            if not customer.code_used_complete:
                history = HistoryCustomerInvitation.objects.filter(is_pending=True, used_by=customer)
                # import pdb; pdb.set_trace()
                # Create free shipping to the user who invites with their code
                if history.exists():
                    history_temp = history[0]
                    now = timezone.localtime(timezone.now())
                    invitation = CustomerPromotion.objects.create(
                        name="Envío gratis",
                        description="Tienes un envío gratis, para utilizarlo en tu proxíma compra ",
                        customer=customer,
                        history=history_temp,
                        created_at=now,
                        expiration_date=now + timedelta(days=10)
                    )
                    # Create free shipping to the user who invites with their code
                    invitation_issued = CustomerPromotion.objects.create(
                        name="Envío gratis",
                        description="Tienes un envío gratis, para utilizarlo en tu proxíma compra ",
                        customer=history_temp.issued_by,
                        history=history_temp,
                        created_at=now,
                        expiration_date=now + timedelta(days=10)
                    )
                    history_temp.is_pending = False
                    history_temp.save()

                    # Send notifications
                    send_notification_push_order(user_id=history_temp.issued_by.user_id,
                                                 title='¡Tienes un envío gratis!',
                                                 body='{} ha utilizado tu código de referido'.format(customer.name),
                                                 sound="default",
                                                 android_channel_id="messages",
                                                 data={"type": "INVITATIONS",
                                                       'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                       })
                    customer.code_used_complete = True
                    customer.save()

        except ValueError as e:
            print(e.args.__str__())
            raise ValueError('Error al validar la invitación')
        except Exception as ex:
            print("Exception in validation invitation, please check it")
            print(ex.args.__str__())
            raise ValueError('Error al validar la invitación')


class UpdateOrderStatusSerializer(serializers.Serializer):
    service = serializers.SlugRelatedField(slug_field="slug_name", queryset=Service.objects.all())
    order_status = serializers.SlugRelatedField(slug_field="slug_name", queryset=OrderStatus.objects.all())

    def update(self, instance, data):
        try:

            instance = update_order_status(service=data['service'],
                                           order_status=data['order_status'],
                                           instance=instance,
                                           data=get_data_notification(data['order_status'].slug_name)
                                           )
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in update order status, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al cambiar de estatus el pedido'})


def update_order_status(service, order_status, instance, data):
    try:
        # Validate that status
        if instance.service.slug_name != service.slug_name:
            raise ValueError('No es posible cambiar de estatus esta orden, no corresponde el tipo del servicio')

        # Validate that status are not "order_status_slug"
        # if instance.order_status == order_status_slug:
        #     raise ValueError('El estatus fue cambiado anteriormente')

        # Update order status
        # order_status = OrderStatus.objects.get(slug)
        instance.order_status = order_status
        instance.save()

        if data['type'] == 'in_the_commerce' and instance.is_order_to_merchant:
            send_notification_push_order_with_sound(user_id=instance.merchant.user_id,
                                                    title='El repartidor esta esperando el pedido',
                                                    body='Numero de pedido {}'.format(instance.qr_code),
                                                    sound="claxon.mp3",
                                                    android_channel_id="claxon",
                                                    data={"type": "UPDATE_ORDER_STATUS",
                                                          "order_id": instance.id,
                                                          "message": "Esperando",
                                                          'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                          })
        elif data['type'] == 'already_here':
            send_notification_push_order_with_sound(user_id=instance.user_id,
                                                    title='El scooter acaba de llegar ',
                                                    body='El scooter te esta esperando'.format(instance.qr_code),
                                                    sound="claxon.mp3",
                                                    android_channel_id="claxon",
                                                    data={"type": "UPDATE_ORDER_STATUS",
                                                          "order_id": instance.id,
                                                          "message": "Esperando",
                                                          'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                          })
        else:
            send_notification_push_task.delay(instance.user_id,
                                              data['title'],
                                              data['body'],
                                              {"type": data['type'], "order_id": instance.id,
                                               "message": data['body'],
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                               })
        # Notification.objects.create(user_id=instance.user_id, title="En camino al comercio",
        #                             type_notification_id=1,
        #                             body="Tu pedido ya esta en camino de ser comprado")
        return instance
    except ValueError as e:
        raise ValueError(e)
    except Exception as ex:
        raise ValueError(ex)


def get_data_notification(status_slug_name):
    # Switch case python
    sw_purchase = {
        'way_commerce': {
            "title": 'En el lugar de entrega',
            "body": 'Tu scooter ha llegado',
            "type": "UPDATE_ORDER_STATUS"
        },
        'in_the_commerce': {
            "title": 'Tu scooter ya esta en la tienda',
            "body": 'Te avisaremos cuando ya tengamos tus productos',
            "type": "UPDATE_ORDER_STATUS"
        },
        'delivery_process': {
            "title": 'Ya tenemos tus productos',
            "body": 'Tu scooter ya va en camino a entregarlos',
            "type": "UPDATE_ORDER_STATUS"
        },
        'already_here': {
            "title": 'Tu scooter te esta esperando afuera',
            "body": 'Tu scooter esta esperando afuera con tu pedido',
            "type": "UPDATE_ORDER_STATUS"
        },
        'location_pick_up': {
            "title": 'En el lugar de recolección',
            "body": 'Tu scooter ya esta recogiendo los productos',
            "type": "UPDATE_ORDER_STATUS"
        },
        'delivery_process_pickup': {
            "title": 'En proceso de entrega',
            "body": 'Tu scooter ya recogio los productos',
            "type": "UPDATE_ORDER_STATUS"
        }

    }

    return sw_purchase.get(status_slug_name, 'default')


def get_message_accept(order):
    if order.is_safe_order or order.is_order_to_merchant:
        return {
            'title': 'En camino al comercio',
            'body': 'Tu scooter ya va en camino al comercio',
            'status_slug': 'way_commerce'
        }
    else:
        return {
            'title': 'Repartidor en camino',
            'body': 'El repartidor ya va en camino a recoger el dinero para la compra',
            'status_slug': 'go_money'
        }
