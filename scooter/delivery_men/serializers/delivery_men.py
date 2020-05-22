""" Users serializers """
# General
from datetime import timedelta
from django.utils import timezone
# Django rest framework
from rest_framework import serializers
# Models
from scooter.users.models import User, Station
from scooter.delivery_men.models import DeliveryMen
# Utilities
# Serializers
from scooter.common.serializers.common import Base64ImageField
from scooter.users.serializers.users import UserModelSimpleSerializer


class DeliveryMenModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryMen
        fields = '__all__'


class DeliveryManUserModelSerializer(serializers.ModelSerializer):
    user = UserModelSimpleSerializer()

    class Meta:
        model = DeliveryMen
        fields = '__all__'
        read_only_fields = (
            'reputation',
        )


class CreateDeliveryMenSerializer(serializers.Serializer):

    picture = Base64ImageField(required=False)
    password = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=60)
    last_name = serializers.CharField(max_length=60)
    phone_number = serializers.CharField(max_length=15)
    salary_per_order = serializers.FloatField(default=0)

    def validate(self, data):
        user_exist = User.objects.filter(username=data['phone_number']).exists()
        if user_exist:
            raise serializers.ValidationError({'detail': 'Ya se encuentra un repartidor con ese numero de telefono'},
                                              code='delivery_exist')
        return data

    def create(self, data):
        try:
            station = self.context['station']
            user = User(username=data['phone_number'],
                        is_client=False,
                        is_verified=True,
                        verification_deadline=timezone.now())

            user.set_password(data['password'])
            user.save()

            delivery_man = DeliveryMen.objects.create(name=data['name'],
                                                      last_name=data['last_name'],
                                                      phone_number=data['phone_number'],
                                                      user=user,
                                                      station=station)
            # in the future send an email to the station when a new delivery man register
            return delivery_man
        except Exception as ex:
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Ha ocurrido un problema al registrarse un repartidor'})