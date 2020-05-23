""" Common status serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.models.status import Status


class StatusModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = ('id', 'name', 'slug_name')
