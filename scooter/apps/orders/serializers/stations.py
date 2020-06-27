# Rest framework
from rest_framework import serializers
# Serializers
# Models
from scooter.apps.common.models import OrderStatus
from scooter.apps.delivery_men.models import DeliveryMan
# Functions channels
# Task Celery
from scooter.apps.taskapp.tasks import send_notification_push_task
# Functions
from scooter.apps.orders.serializers.orders import get_nearest_delivery_man
# Serializers primary field
from scooter.apps.common.serializers.common import StationFilteredPrimaryKeyRelatedField
# Task Celery
from scooter.apps.taskapp.tasks import send_notification_push_task


class AssignDeliveryManStationSerializer(serializers.Serializer):
    delivery_man_id = StationFilteredPrimaryKeyRelatedField(queryset=DeliveryMan.objects,
                                                            source="delivery_man")

    def update(self, instance, data):
        try:
            delivery_man = data['delivery_man']
            send_notification_push_task.delay(delivery_man.user.id, 'Solicitud nueva por la central',
                                              'Pedido de compra', {"type": "NEW_ORDER", "order_id": instance.id})
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al rechazar el pedido'})


class RejectOrderStationSerializer(serializers.Serializer):
    reason_rejection = serializers.CharField(max_length=100)

    def update(self, instance, data):
        try:
            customer = instance.customer
            instance.reason_rejection = data['reason_rejection']
            # Filter for type_service
            order_sts = OrderStatus.objects.get(slug_name="rejected")
            instance.order_status = order_sts
            instance.save()
            send_notification_push_task.delay(customer.user.id, 'Pedido rechazado',
                                              'Se ha rechazado tu pedido',
                                              {"type": "REJECT_ORDER",
                                               "order_id": instance.id,
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'})
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al rechazar el pedido'})

