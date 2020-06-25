# Rest framework
from rest_framework import serializers
# Serializers
# Models
from scooter.apps.delivery_men.models import DeliveryMan
# Functions channels
# Task Celery
from scooter.apps.taskapp.tasks import send_notification_push_task
# Functions
from scooter.apps.orders.serializers.orders import get_nearest_delivery_man
# Serializers primary field
from scooter.apps.common.serializers.common import StationFilteredPrimaryKeyRelatedField


class AssignDeliveryManStationSerializer(serializers.Serializer):
    delivery_man_id = StationFilteredPrimaryKeyRelatedField(queryset=DeliveryMan.objects, source="delivery_man")

    def update(self, instance, data):
        try:
            varia = 1
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in reject order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al rechazar el pedido'})


class RejectOrderStationSerializer(serializers.Serializer):
    pass
