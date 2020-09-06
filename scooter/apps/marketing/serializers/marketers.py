""" Marketers serializers """
# General
from django.utils import timezone
# Django rest framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# Models
from scooter.apps.users.models import User
from scooter.apps.marketing.models.marketers import Marketer
# Serializers
from scooter.apps.users.serializers.users import UserModelSimpleSerializer


class MarketerUserSimpleSerializer(serializers.ModelSerializer):

    user = UserModelSimpleSerializer()

    class Meta:
        model = Marketer
        fields = '__all__'


class MarketerSignUpSerializer(serializers.Serializer):
    """ Serializer only to register a new merchant """
    username = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='El email ya esta en uso')])
    password = serializers.CharField(max_length=50)
    full_name = serializers.CharField(max_length=120)
    phone_number = serializers.CharField(max_length=15)

    def create(self, data):
        try:
            user = User(username=data.pop('username'),
                        is_verified=True,
                        role=User.MARKETER,
                        is_client=False,
                        verification_deadline=timezone.localtime(timezone.now()))
            password = data.pop('password')
            user.set_password(password)
            user.save()
            Marketer.objects.create(**data, user=user)
            # code = generate_verification_token(user=user,
            #                                    exp=timezone.localtime(timezone.now()) + timedelta(minutes=20),
            #                                    token_type='email_confirmation')

            # subject = 'Bienvenido {name}'.format(name=merchant.merchant_name)
            # data = {
            #     'email': user.username,
            #     'name': merchant.merchant_name,
            #     'password': password,
            #     'url': settings.URL_SERVER_FRONTEND
            # }
            # send_email = send_mail_verification(subject=subject,
            #                                     to_user=user.username,
            #                                     path_template="emails/merchants/welcome.html",
            #                                     data=data)
            # if not send_email:
            #     raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar el correo'})
            # return user
            return data
        except Exception as ex:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un problema al registrarse'})
