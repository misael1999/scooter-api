""" Common status serializers """
# Django rest framework
import random
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


class StationSupportMessage(serializers.ModelSerializer):

    def create(self, validated_data):
        pass
