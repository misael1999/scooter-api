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


class NotifyAllCustomersSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=80)
    body = serializers.CharField(max_length=300)

    def create(self, data):
        try:
            customers = Customer.objects.all()
            for customer in customers:
                send_notification_push_order(customer.user_id, data['title'],
                                             body=data['body'],
                                             sound="default",
                                             android_channel_id="messages",
                                             data={})
            return data
        except Exception as ex:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar las notificaciones a los usuarios'})


class NotifyAllMerchantsSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=80)
    body = serializers.CharField(max_length=300)

    def create(self, data):
        try:
            merchants = Merchant.objects.all()
            for merchant in merchants:
                send_notification_push_order(merchant.user_id, data['title'],
                                             body=data['body'],
                                             sound="default",
                                             android_channel_id="messages",
                                             data={})
            return data
        except Exception as ex:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar las notificaciones a lo comercios'})


class NotifyAllDeliverySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=50)
    body = serializers.CharField(max_length=100)

    def create(self, data):
        delivery_men = DeliveryMan.objects.all()
        for delivery in delivery_men:
            send_notification_push_order(delivery.user_id, data['title'],
                                         body=data['body'],
                                         sound="default",
                                         android_channel_id="locations",
                                         data={})
        return data
