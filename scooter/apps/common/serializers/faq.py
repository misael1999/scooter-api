""" Common status serializers """
# Django rest framework
from django.conf import settings
from rest_framework import serializers
# Models
from scooter.apps.common.models.faq import Question
from scooter.apps.payments.models.cards import Card, CustomerConekta
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer
import conekta


class QuestionSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'title', 'answer', 'status', 'created')
        read_only_fields = fields


class QuestionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ('id', 'title', 'answer', 'status')
        read_only_fields = ('id',)
