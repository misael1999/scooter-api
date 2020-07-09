# Rest framework
from rest_framework import serializers
from django.utils import timezone
# Serializers
# Models
from scooter.apps.common.models import DeliveryManStatus, OrderStatus, Notification
from scooter.apps.orders.models.orders import HistoryRejectedOrders
# Functions channels
# Task Celery
from scooter.apps.taskapp.tasks import send_notification_push_task
# Functions
from scooter.apps.orders.serializers.orders import get_nearest_delivery_man


class AcceptOrderByDeliveryManSerializer(serializers.Serializer):

    def validate(self, data):
        order = self.context['order']
        delivery_man = self.context['delivery_man']
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
            if instance.service.slug_name == 'pick_up':
                order_status = OrderStatus.objects.get(slug_name='pick_up')
            else:
                order_status = OrderStatus.objects.get(slug_name='go_money')
            order.order_status = order_status
            # Assign order to delivery man
            order.delivery_man = delivery_man
            order.save()
            # Send notification push to customer
            send_notification_push_task.delay(order.customer.user.id,
                                              'Repartidor en camino',
                                              'Puedes ver el seguimiento de tu producto',
                                              {"type": "ACCEPTED_ORDER",
                                               "order_id": order.id,
                                               "message": "Puedes ver el seguimiento de tu producto",
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                               })
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

            send_notification_push_task.delay(delivery_man.user.id,
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


class OnGoMoneyPurchaseSerializer(serializers.Serializer):
    """ On the way to collect the purchase money """

    def update(self, instance, data):
        try:
            data_notification = {
                "title": 'Pedido aceptado',
                "body": 'El repartidor ya va en camino recoger el dinero de la compra',
                "type": "GO_MONEY"
            }
            instance = update_order_status(type_service="purchase",
                                           order_status_slug="go_money",
                                           instance=instance,
                                           data=data_notification
                                           )
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in on way trader order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al cambiar de estatus el pedido'})


# Serializer for change order status
class OnWayCommercePurchaseSerializer(serializers.Serializer):
    """ On the way to the commerce to buy the products """

    def update(self, instance, data):
        try:
            data_notification = {
                "title": 'En camino al comercio',
                "body": 'El repartidor ya va en camino a comprar los productos',
                "type": "WAY_COMMERCE"
            }
            instance = update_order_status(type_service="purchase",
                                           order_status_slug="way_commerce",
                                           instance=instance,
                                           data=data_notification
                                           )
            # Notification.objects.create(user_id=instance.user_id, title="En camino al comercio",
            #                             type_notification_id=1,
            #                             body="Tu pedido ya esta en camino de ser comprado")
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in on way trader order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al cambiar de estatus el pedido'})


class OnDeliveryProcessPurchaseSerializer(serializers.Serializer):

    def update(self, instance, data):
        try:
            data_notification = {
                "title": 'Ya tenemos tus productos',
                "body": 'El repartidor ya va en camino a entregarlos',
                "type": "DELIVERY_PROCESS"
            }
            instance = update_order_status(type_service="purchase",
                                           order_status_slug="delivery_process",
                                           instance=instance,
                                           data=data_notification
                                           )
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in on delivery process, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al cambiar de estatus el pedido'})


class ScanQrOrderSerializer(serializers.Serializer):
    """ Scan qr to mark the order as delivered """

    qr_code = serializers.CharField(max_length=10)

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
                "type": "RATING_DELIVERY"
            }
            instance = update_order_status(type_service="purchase",
                                           order_status_slug="delivered",
                                           instance=instance,
                                           data=data_notification
                                           )
            instance.date_delivered_order = timezone.localtime(timezone.now())
            instance.save()

            Notification.objects.create(user_id=instance.user_id, title="Califica tu pedido",
                                        type_notification_id=1,
                                        body="Tu pedido ha sido entregado, deja una calificación")
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al escanear el código'})


def update_order_status(type_service, order_status_slug, instance, data):
    try:
        # Validate that status
        if instance.service.slug_name != type_service:
            raise ValueError('No es posible cambiar de estatus')

        # Validate that status are not "order_status_slug"
        if instance.order_status == order_status_slug:
            raise ValueError('El estatus fue cambiado anteriormente')

        # Update order status
        order_status = OrderStatus.objects.get(slug_name=order_status_slug)
        instance.order_status = order_status
        instance.save()

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