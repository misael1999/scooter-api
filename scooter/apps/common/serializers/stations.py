""" Common status serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.models.common import Service, Schedule


class ServiceModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ('id', 'name', 'slug_name')


class ScheduleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Schedule
        fields = ('id', 'name', 'slug_name')

