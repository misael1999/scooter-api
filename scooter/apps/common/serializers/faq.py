""" Common status serializers """
# Django rest framework
from django.conf import settings
from rest_framework import serializers
# Models
from scooter.apps.common.models.faq import Question, GroupQuestion
from scooter.apps.payments.models.cards import Card, CustomerConekta
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer
import conekta


class QuestionSimpleSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'title', 'answer', 'group', 'group_id', 'status', 'created')
        read_only_fields = fields


class QuestionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ('id', 'title', 'answer', 'group')
        read_only_fields = ('id',)


class GroupQuestionSimpleSerializer(serializers.ModelSerializer):
    questions = QuestionSimpleSerializer(read_only=True, many=True)

    class Meta:
        model = GroupQuestion
        fields = ('id', 'name', 'questions', 'created')
        read_only_fields = ('id', 'questions', 'created')
