# Rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.models import OrderStatus, DeliveryManStatus
from scooter.apps.delivery_men.models import DeliveryMan
# Serializers primary field
from scooter.apps.common.serializers.common import StationFilteredPrimaryKeyRelatedField
# Task Celery
from scooter.apps.orders.serializers import get_message_accept, accept_order_devivery
from scooter.apps.taskapp.tasks import send_notification_push_task


class AssignDeliveryManStationSerializer(serializers.Serializer):
    delivery_man_id = StationFilteredPrimaryKeyRelatedField(queryset=DeliveryMan.objects,
                                                            source="delivery_man")

    def update(self, order, data):
        try:
            delivery_man = data['delivery_man']
            if order.delivery_man:
                raise ValueError('El pedido ya tiene repartidor')
            accept_order_devivery(order=order, delivery_man=delivery_man)
            send_notification_push_task.delay(user_id=delivery_man.user.id,
                                              title='Pedido asignado por la central',
                                              body='Revisa tu lista de pedidos',
                                              sound="ringtone.mp3",
                                              data={"type": "ORDER_ASSIGNED",
                                                    "order_id": order.id,
                                                    'click_action': 'FLUTTER_NOTIFICATION_CLICK'},
                                              android_channel_id="alarms")

            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al asignar el pedido'})


class ReassignDeliveryManStationSerializer(serializers.Serializer):
    delivery_man_id = StationFilteredPrimaryKeyRelatedField(queryset=DeliveryMan.objects,
                                                            source="delivery_man")

    def update(self, order, data):
        try:
            delivery_man = data['delivery_man']
            if order.delivery_man == delivery_man:
                raise ValueError('El pedido ya esta asignado a {}'.format(delivery_man.name))
            order.delivery_man = delivery_man
            order.save()
            send_notification_push_task.delay(user_id=delivery_man.user.id,
                                              title='Pedido asignado por la central',
                                              body='Revisa tu lista de pedidos',
                                              sound="ringtone.mp3",
                                              data={"type": "ORDER_ASSIGNED",
                                                    "order_id": order.id,
                                                    'click_action': 'FLUTTER_NOTIFICATION_CLICK'},
                                              android_channel_id="alarms")

            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al asignar el pedido'})


class RejectOrderStationSerializer(serializers.Serializer):
    reason_rejection = serializers.CharField(max_length=100)

    def update(self, instance, data):
        try:
            customer = instance.customer
            instance.reason_rejection = data['reason_rejection']
            # Filter for type_service
            order_sts = OrderStatus.objects.get(slug_name="rejected")
            instance.order_status = order_sts
            instance.in_process = False
            instance.save()
            send_notification_push_task.delay(user_id=customer.user.id,
                                              title='Pedido rechazado',
                                              body='Se ha rechazado tu pedido',
                                              sound="default",
                                              data={"type": "REJECT_ORDER",
                                                    "order_id": instance.id,
                                                    'click_action': 'FLUTTER_NOTIFICATION_CLICK'},
                                              android_channel_id="messages")
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al rechazar el pedido'})


class CancelOrderStationSerializer(serializers.Serializer):
    reason_rejection = serializers.CharField(max_length=100)

    def update(self, instance, data):
        try:
            customer = instance.customer
            instance.reason_rejection = data['reason_rejection']
            # Filter for type_service
            order_sts = OrderStatus.objects.get(slug_name="cancelled")
            instance.order_status = order_sts
            instance.in_process = False
            instance.save()
            send_notification_push_task.delay(user_id=customer.user.id,
                                              title='Pedido cancelado por la central',
                                              body='Se ha cancelo tu pedido por {}'.format(data['reason_rejection']),
                                              sound="default",
                                              data={"type": "REJECT_ORDER",
                                                    "order_id": instance.id,
                                                    'click_action': 'FLUTTER_NOTIFICATION_CLICK'},
                                              android_channel_id="messages")
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al cancelar el pedido'})
