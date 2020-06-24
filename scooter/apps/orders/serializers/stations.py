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


class AssignDeliveryManStationSerializer(serializers.Serializer):
    pass


class RejectOrderStationSerializer(serializers.Serializer):
    pass
