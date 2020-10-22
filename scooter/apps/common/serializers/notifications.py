""" Notifications serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.models import Notification
from scooter.apps.customers.models import Customer
# Functions
from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.merchants.models import Merchant
from scooter.utils.functions import send_notification_push_order


class NotificationModelSerializer(serializers.ModelSerializer):
    type_notification = serializers.StringRelatedField()

    class Meta:
        model = Notification
        fields = (
            'id', 'title', 'body', 'action', 'payload',
            'type_notification', 'user'
        )
        read_only_fields = fields


class NotifyAllSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=80)
    body = serializers.CharField(max_length=300)
    type = serializers.IntegerField(default=1, required=False)

    def create(self, data):
        try:
            query_set = Merchant.objects.all()
            if data['type'] == 2:
                query_set = DeliveryMan.objects.filter(status__slug_name="active")
            elif data['type'] == 3:
                query_set = Merchant.objects.filter(status__slug_name="active")

            for user in query_set:
                send_notification_push_order(user.user_id, data['title'],
                                             body=data['body'],
                                             sound="default",
                                             android_channel_id="messages",
                                             data={})

            return data
        except Exception as ex:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar las notificaciones'})
