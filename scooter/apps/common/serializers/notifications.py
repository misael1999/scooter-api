""" Notifications serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.models import Notification


class NotificationModelSerializer(serializers.ModelSerializer):

    type_notification = serializers.StringRelatedField()

    class Meta:
        model = Notification
        fields = (
            'id', 'title', 'body', 'action', 'payload',
            'type_notification', 'user'
        )
        read_only_fields = fields
