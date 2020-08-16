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


class AcceptOrderMerchantSerializer(serializers.Serializer):

    def update(self, instance, data):
        try:
            order_status = OrderStatus.objects.get(slug_name="preparing_order")
            instance.order_status = order_status
            instance.save()
            send_notification_push_task.delay(instance.user_id, 'Pedido aceptado',
                                              'Se ha aceptado el pedido por parte del comercio', {"type": "NEW_ORDER", "order_id": instance.id})
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al rechazar el pedido'})


class RejectOrderMerchantSerializer(serializers.Serializer):
    reason_rejection = serializers.CharField(max_length=100, required=True, allow_null=True)

    def update(self, instance, data):
        pass


class CancelOrderMerchantSerializer(serializers.Serializer):
    reason_rejection = serializers.CharField(max_length=100, required=True, allow_null=True)

    def update(self, instance, data):

        pass
