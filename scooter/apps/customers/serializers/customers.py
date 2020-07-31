""" Customers serializers """
# Django
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
# Django rest framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# Models
from scooter.apps.common.models import Notification
from scooter.apps.users.models import User
from scooter.apps.customers.models.customers import Customer
# Utilities
from scooter.utils.functions import send_mail_verification, generate_verification_token
# Serializers
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
from scooter.apps.common.serializers import Base64ImageField


class CustomerSimpleModelSerializer(serializers.ModelSerializer):
    picture = Base64ImageField(max_length=None, required=False, use_url=True)
    user = UserModelSimpleSerializer()

    class Meta:
        model = Customer
        fields = (
            'id',
            'user',
            'name',
            'birthdate',
            'picture',
            'picture_url',
            'phone_number',
            'reputation',
            'is_safe_user'
        )

    def update(self, instance, data):
        """ Before updating we have to delete the previous image """
        try:
            if data['picture']:
                instance.picture.delete(save=True)
        except Exception as ex:
            print("Exception deleting image client, please check it")
            print(ex.args.__str__())
        return super().update(instance, data)


class CustomerSimpleOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = (
            'id',
            'name',
            'phone_number',
            'reputation',
            'is_safe_user'
        )
        read_only_fields = fields


class CustomerUserModelSerializer(serializers.ModelSerializer):
    user = UserModelSimpleSerializer()
    picture = Base64ImageField(use_url=True)

    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = (
            'reputation',
        )


class CustomerSignUpSerializer(serializers.Serializer):
    username = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='El email ya esta en uso')])

    name = serializers.CharField(max_length=60)
    password = serializers.CharField(min_length=8, max_length=64)
    birthdate = serializers.DateField(required=False)
    picture = Base64ImageField(required=False)
    phone_number = serializers.CharField(max_length=15, required=False)

    def create(self, data):
        user = User(username=data['username'],
                    is_verified=False,
                    is_client=True,
                    role=User.CUSTOMER,
                    verification_deadline=timezone.localtime(timezone.now()) + timedelta(days=1))
        user.set_password(data['password'])
        user.save()
        customer = Customer.objects.create(user=user,
                                           name=data['name'])

        code = generate_verification_token(user=user,
                                           exp=user.verification_deadline,
                                           token_type='email_confirmation')
        subject = 'Bienvenido {name}, Verifica tu cuenta para comenzar'.format(name=customer.name)
        # Create a notification
        Notification.objects.create(user=user, title="Bienvenido",
                                    type_notification_id=1,
                                    body="Te enviamos un correo para validar tu cuenta")
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
        return customer


class ChangePasswordCustomerSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=60)
    new_password = serializers.CharField(min_length=8, max_length=60)

    def update(self, instance, data):
        try:
            # Check if current_password is correct
            if not instance.user.check_password(data['current_password']):
                raise ValueError('La contraseña actual no es correcta')

            instance.user.set_password(data['new_password'])
            instance.user.save()
            return instance
        except ValueError as ex:
            raise serializers.ValidationError({'detail': str(ex)})
        except Exception as e:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error desconocido'})

