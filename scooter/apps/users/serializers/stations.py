""" Users serializers """
# General
from datetime import timedelta
from django.utils import timezone
# Django
from django.conf import settings
# Django rest framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# Models
from scooter.apps.users.models import User, Station
# Utilities
from scooter.utils.functions import send_mail_verification, generate_verification_token
# Serializers
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
from scooter.apps.common.serializers import Base64ImageField


class StationSimpleModelSerializer(serializers.ModelSerializer):
    picture = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = Station
        fields = '__all__'
        read_only_fields = (
            'reputation',
            'total_orders',
            'total_clients',
            'total_delivery_man',
            'total_messages_support',
            'station_verified',
            'user',
            'station_name',
        )

    def update(self, instance, validated_data):
        """ Before updating we have to delete the previous image """
        try:
            instance.picture.delete(save=True)
        except Exception as ex:
            print("Exception deleting image client, please check it")
            print(ex.args.__str__())
        return super().update(instance, validated_data)


class StationUserModelSerializer(serializers.ModelSerializer):
    user = UserModelSimpleSerializer()

    class Meta:
        model = Station
        exclude = ('created', 'modified')
        read_only_fields = (
            'reputation',
            'total_orders',
            'total_clients',
            'total_delivery_man',
            'total_messages_support',
            'station_verified',
            'user',
            'station_name',
        )


class StationSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='El email ya esta en uso')])

    contact_person = serializers.CharField(max_length=60)
    password = serializers.CharField(min_length=8, max_length=64)
    station_name = serializers.CharField(max_length=100, validators=[UniqueValidator(
        queryset=Station.objects.all(),
        message='Ya existe una central con el mismo nombre. ¿La central es tuya?')])

    def create(self, data):
        try:
            user = User(username=data['username'],
                        is_verified=False,
                        is_client=False,
                        verification_deadline=timezone.now() + timedelta(minutes=20))
            user.set_password(data['password'])
            user.save()
            station = Station.objects.create(user=user,
                                             contact_person=data['contact_person'],
                                             station_name=data['station_name'],
                                             )

            code = generate_verification_token(user=user,
                                               exp=timezone.now() + timedelta(minutes=20),
                                               token_type='email_confirmation')

            subject = 'Bienvenido {name}, Verifica tu cuenta para comenzar'.format(name=station.station_name)
            data = {
                'user': user,
                'token': code,
                'url': settings.URL_SERVER_FRONTEND
            }
            send_email = send_mail_verification(subject=subject,
                                                to_user=user.username,
                                                path_template="emails/users/account_verification.html",
                                                data=data)
            if not send_email:
                raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar el correo'})
            return user

        except Exception as ex:
            return serializers.ValidationError({'detail': 'Ha ocurrido un problema al registrarse'})
