""" Customers serializers """

# Django
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
# Django rest framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# Models
from scooter.users.models import User, Customer
# Utilities
from scooter.utils.functions import send_mail_verification, generate_verification_token
# Serializers
from scooter.users.serializers.users import UserModelSimpleSerializer
from scooter.common.serializers.common import Base64ImageField


class CustomerSimpleModelSerializer(serializers.ModelSerializer):
    picture = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = (
            'reputation',
            'created',
            'modified',
            'status',
            'user'
        )

    def update(self, instance, validated_data):
        """ Before updating we have to delete the previous image """
        try:
            instance.picture.delete(save=True)
        except Exception as ex:
            print("Exception deleting image client, please check it")
            print(ex.args.__str__())
        return super().update(instance, validated_data)


class CustomerUserModelSerializer(serializers.ModelSerializer):
    user = UserModelSimpleSerializer()

    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = (
            'reputation',
        )


class CustomerSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='El email ya esta en uso')])

    name = serializers.CharField(max_length=60)
    last_name = serializers.CharField(max_length=60)
    password = serializers.CharField(min_length=8, max_length=64)
    birthdate = serializers.DateField()
    picture = Base64ImageField(required=False)

    def create(self, data):
        user = User(email=data['email'],
                    is_verified=False,
                    is_client=True,
                    verification_deadline=timezone.now() + timedelta(days=1))
        user.set_password(data['password'])
        user.save()
        customer = Customer.objects.create(user=user,
                                           birthdate=data['birthdate'],
                                           name=data['name'],
                                           last_name=data['last_name'])
        code = generate_verification_token(user=user,
                                           exp=user.verification_deadline,
                                           token_type='email_confirmation')
        subject = 'Bienvenido {name}, Verifica tu cuenta para comenzar'.format(name=customer.name)
        data = {
            'user': user,
            'token': code,
            'url': settings.URL_SERVER_FRONTEND
        }
        send_email = send_mail_verification(subject=subject,
                                            to_user=user.email,
                                            path_template="emails/users/account_verification.html",
                                            data=data)
        if not send_email:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar el correo'})
        return customer
