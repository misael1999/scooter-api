""" Common status serializers """
# Django rest framework
import random
from django.utils import timezone
from string import ascii_uppercase, digits

from django.conf import settings
from rest_framework import serializers
# Models
from scooter.apps.orders.models import Order
from scooter.apps.orders.serializers.v2 import DetailOrderSerializer, DeliveryManOrderSerializer, \
    OrderStatusModelSerializer, CardModelSerializer
from scooter.apps.payments.models.cards import Card, CustomerConekta
# Utilities
from scooter.apps.stations.models import Station
from scooter.apps.support.models import Support, SupportMessage
from scooter.utils.serializers.scooter import ScooterModelSerializer


class CloseOrOpenSupportSerializer(serializers.Serializer):
    is_open = serializers.BooleanField()

    def update(self, support, data):
        try:
            support.is_open = data['is_open']
            support.finish_date = timezone.localtime(timezone.now())
            support.support_status_id = 2
            support.save()
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create support message, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al guardar el mensaje'})


class StationSupportMessage(serializers.ModelSerializer):

    def create(self, validated_data):
        pass
