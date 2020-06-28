# Rest framework
from rest_framework import serializers
# Serializers
# Models
from scooter.apps.common.models import DeliveryManStatus, OrderStatus
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
            order_status = OrderStatus.objects.get(slug_name='process_money')
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
