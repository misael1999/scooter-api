""" Common status serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.models.status import Status
# Serializer


class StatusModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = '__all__'
