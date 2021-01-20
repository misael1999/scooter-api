# Rest framework
from datetime import timedelta

from django.conf import settings
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
from scooter.apps.orders.serializers.v2 import OrderWithDetailModelSerializer
from scooter.apps.support.models import Support
from scooter.apps.taskapp.tasks import send_notification_push_task, send_email_task
# Functions
from scooter.apps.orders.serializers.orders import get_nearest_delivery_man
# Functions channels
from scooter.apps.orders.utils.orders import notify_station_accept
from scooter.apps.orders.utils.orders import notify_delivery_men
from asgiref.sync import async_to_sync

from scooter.utils.functions import send_notification_push_order, send_notification_push_order_with_sound
# Conekta
import conekta

conekta.api_key = settings.CONEKTA_API_KEY
conekta.api_version = settings.CONEKTA_API_VERSION


class AcceptOrderByDeliveryManSerializer(serializers.Serializer):

    def validate(self, data):
        order = self.context['order']
        delivery_man = self.context['delivery_man']

        data['order'] = order
        data['delivery_man'] = delivery_man

        if order.delivery_man == delivery_man:
            return data

        if order.order_status.slug_name == 'rejected':
            raise serializers.ValidationError({'detail': 'El pedido fue rechazado, el tiempo de espera culmino'},
                                              code='order_already_delivery_man')

        # Verify that the order does not have a delivery man assigned
        if order.delivery_man is not None:
            raise serializers.ValidationError({'detail': 'El pedido ya tiene un repartidor asignado'},
                                              code='order_already_delivery_man')

        return data

    def update(self, instance, data):
        try:
            delivery_man = data['delivery_man']
            order = data['order']
            if order.delivery_man == delivery_man:
                return data
            accept_order_devivery(order=order, delivery_man=delivery_man)

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

    def update(self, order, data):
        try:
            data_notification = {
                "title": 'Pedido entregado, por favor califica tu pedido 🛵 🛴',
                "body": 'Tu pedido ha sido entregado, deja un comentario 👍🏻',
                "type": "ORDER_DELIVERED"
            }
            # Update member station
            # station = order.station
            customer = order.customer
            self.generate_free_delivery(customer=customer)

            order = update_order_status(service=data['service'],
                                        order_status=OrderStatus.objects.get(slug_name="delivered"),
                                        instance=order,
                                        data=data_notification
                                        )

            order.date_delivered_order = timezone.localtime(timezone.now())
            order.in_process = False
            order.save()

            # Recuperar el id del soporte
            try:
                support = order.supports.first()
                if support:
                    support.is_open = False
                    support.status_id = 2
                    support.save()
            except Support.DoesNotExist:
                pass
            except Exception as ex:
                pass

            delivery_status = DeliveryManStatus.objects.get(slug_name="available")
            delivery_man = order.delivery_man
            delivery_man.delivery_status = delivery_status
            delivery_man.save()
            if order.is_order_to_merchant:
                # Capturar el pago preautorizado
                if order.is_payment_online:
                    try:
                        order_conekta = conekta.Order.find(order.order_conekta_id)
                        order_captured = order_conekta.capture()
                    except conekta.ConektaError as e:
                        # Mandar notificación de manera temporal
                        # Agregar una tabla con pagos no realizados psra reintentar
                        send_notification_push_task.delay(user_id=order.station.user.id,
                                                          title='Cobro no realizodo',
                                                          body="No se ha realizo el cobro del pedido con el numero 123",
                                                          sound="default",
                                                          android_channel_id="messages",
                                                          data={"type": data['type'],
                                                                "order_id": order.id,
                                                                "message": "Pedido de nuevo",
                                                                'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                                })

                # date_delivered = order.date_delivered_order
                # data_email = {'order': OrderWithDetailModelSerializer(order).data,
                #               'date_delivered_order': date_delivered.strftime(
                #                   "%m/%d/%Y, %H:%M:%S")
                #               }
                # send_email_task.delay(subject="Tu pedido en Los Pedidos",
                #                       to_user=order.user.username,
                #                       path_template='emails/users/invoice_order.html',
                #                       data=data_email)

            # Notification.objects.create(user_id=instance.user_id, title="Califica tu pedido",
            #                             type_notification_id=1,
            #                             body="Tu pedido ha sido entregado, deja una calificación")
            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in scan qr, please check it")
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
        instance.date_update_order = timezone.localtime(timezone.now())
        instance.save()

        if order_status.slug_name == 'in_the_commerce' and instance.is_order_to_merchant:
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
            send_notification_push_task.delay(user_id=instance.user_id,
                                              title=data['title'],
                                              body=data['body'],
                                              sound="default",
                                              android_channel_id="messages",
                                              data={"type": data['type'],
                                                    "order_id": instance.id,
                                                    "message": "Pedido de nuevo",
                                                    'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                    })
        elif order_status.slug_name == 'already_here':
            send_notification_push_order_with_sound(user_id=instance.user_id,
                                                    title='Tu pedirepartidor acaba de llegar ',
                                                    body='El pedirepartidor te esta esperando'.format(instance.qr_code),
                                                    sound="claxon.mp3",
                                                    android_channel_id="claxon",
                                                    data={"type": "UPDATE_ORDER_STATUS",
                                                          "order_id": instance.id,
                                                          "message": "Esperando",
                                                          'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                          })
        else:
            send_notification_push_task.delay(user_id=instance.user_id,
                                              title=data['title'],
                                              body=data['body'],
                                              sound="default",
                                              android_channel_id="messages",
                                              data={"type": data['type'],
                                                    "order_id": instance.id,
                                                    "message": "Pedido de nuevo",
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
            "body": 'Tu Pedirepartidor ha llegado',
            "type": "UPDATE_ORDER_STATUS"
        },
        'in_the_commerce': {
            "title": 'Tu Pedirepartidor ya esta en la tienda',
            "body": 'Te avisaremos cuando ya tengamos tus productos',
            "type": "UPDATE_ORDER_STATUS"
        },
        'delivery_process': {
            "title": 'Ya tenemos tus productos',
            "body": 'Tu Pedirepartidor ya va en camino a entregarlos',
            "type": "UPDATE_ORDER_STATUS"
        },
        'already_here': {
            "title": 'Tu Pedirepartidor te esta esperando afuera',
            "body": 'Tu Pedirepartidor esta esperando afuera con tu pedido',
            "type": "UPDATE_ORDER_STATUS"
        },
        'location_pick_up': {
            "title": 'En el lugar de recolección',
            "body": 'Tu Pedirepartidor ya esta recogiendo los productos',
            "type": "UPDATE_ORDER_STATUS"
        },
        'delivery_process_pickup': {
            "title": 'En proceso de entrega',
            "body": 'Tu Pedirepartidor ya recogio los productos',
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


def accept_order_devivery(order, delivery_man):
    # Update status delivery man
    delivery_status = DeliveryManStatus.objects.get(slug_name='busy')
    delivery_man.delivery_status = delivery_status
    delivery_man.save()

    # Update status order
    if order.service.slug_name == 'pick_up':
        order_status = OrderStatus.objects.get(slug_name='pick_up')
        data_message = {
            'title': "Repartidor en camino",
            'body': "{} está en camino de recolectar tu pedido".format(delivery_man.name)
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
        send_notification_push_task.delay(user_id=order.merchant.user_id,
                                          title="{} está en camino de recolectar el pedido".format(delivery_man.name),
                                          body='Numero de pedido {}'.format(order.qr_code),
                                          sound="default",
                                          android_channel_id="messages",
                                          data={"type": type_notification,
                                                "order_id": order.id,
                                                "message": "Pedido de nuevo",
                                                'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                })

    send_notification_push_task.delay(user_id=order.user_id,
                                      title="{} está en camino de recolectar el pedido".format(delivery_man.name),
                                      body="Tu pedido esta casí listo",
                                      sound="default",
                                      android_channel_id="messages",
                                      data={"type": type_notification,
                                            "order_id": order.id,
                                            "message": "Pedido de nuevo",
                                            'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                            })
    # async_to_sync(notify_station_accept)(order.station_id, order.id)
    # Notify all delivery men that order was accepted
    # async_to_sync(notify_delivery_men)(order.id, 'ORDER_ACCEPTED')
