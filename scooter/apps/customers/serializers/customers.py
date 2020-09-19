""" Customers serializers """
# Utilities
import random
from string import ascii_uppercase, digits
# Django
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
# Django rest framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# Models
from rest_framework_simplejwt.tokens import RefreshToken

from scooter.apps.common.models import Notification
from scooter.apps.users.models import User
from scooter.apps.customers.models.customers import Customer, HistoryCustomerInvitation, CustomerPromotion
# Utilities
from scooter.utils.functions import send_mail_verification, generate_verification_token
# Serializers
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
from scooter.apps.common.serializers import Base64ImageField


class CustomerInvitationSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'id',
            'name',
            'code_share',
        )
        read_only_fields = fields


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
            'code_share',
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
            'code_share',
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
                    is_verified=True,
                    is_client=True,
                    role=User.CUSTOMER,
                    verification_deadline=timezone.localtime(timezone.now()) + timedelta(days=2))
        user.set_password(data['password'])
        user.save()
        code_share = generate_code_to_share()
        customer = Customer.objects.create(user=user,
                                           code_share=code_share,
                                           name=data['name'])

        code = generate_verification_token(user=user,
                                           exp=user.verification_deadline,
                                           token_type='email_confirmation')
        subject = 'Bienvenido a Scooter Envíos {name}'.format(name=customer.name)
        # Create a notification
        # Notification.objects.create(user=user, title="Bienvenido",
        #                             type_notification_id=1,
        #                             body="Te enviamos un correo para validar tu cuenta,"
        #                                  " si no lo encuentras revisa en tu bandeja de SPAM")
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

        refresh = RefreshToken.for_user(user)
        response = dict()
        response['refresh'] = str(refresh)
        response['access'] = str(refresh.access_token)
        response['customer'] = CustomerUserModelSerializer(customer).data
        return response


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


class EnterPromoCodeSerializer(serializers.Serializer):

    code = serializers.CharField(max_length=20)

    def update(self, customer, data):
        try:
            # Verify that the user has not used an invitation code

            customer_exist_list = Customer.objects.filter(code_share=data['code'])

            if customer_exist_list.exists():
                if customer.code_used:
                    raise ValueError('Ya ha usado un código de promocion de referido, no puede usar otro')
                customer_exist = customer_exist_list[0]
                if customer.id == customer_exist.id:
                    raise ValueError('No es posible que usted use su propio código de invitación')
                now = timezone.localtime(timezone.now())
                # We place that it is pending until you complete your first order
                history = HistoryCustomerInvitation.objects.create(
                    issued_by=customer_exist,
                    used_by=customer,
                    code=data['code'],
                    is_pending=True,
                    date=now
                )
                # # Create free shipping to the user who invites with their code
                # invitation = CustomerInvitation.objects.create(
                #     customer=customer,
                #     history=history,
                #     created_at=now,
                #     expiration_date=now + timedelta(days=10)
                # )
                # # Create free shipping to the user who invites with their code
                # invitation_issued = CustomerInvitation.objects.create(
                #     customer=customer_exist,
                #     history=history,
                #     created_at=now,
                #     expiration_date=now + timedelta(days=10)
                # )
                customer.code_used = True
                customer.save()
            else:
                raise ValueError('El código que ha ingresado no existe')
            return data
        except ValueError as ex:
            raise serializers.ValidationError({'detail': str(ex)})
        except Exception as e:
            print('Error in enter promo code, please check it')
            print(e.args.__str__())
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error desconocido'})


def generate_code_to_share():
    try:
        CODE_LENGTH = 7
        """ Handle code creation """
        pool = ascii_uppercase + digits
        code = ''.join(random.choices(pool, k=CODE_LENGTH))
        while Customer.objects.filter(code_share=code).exists():
            code = ''.join(random.choices(pool, k=CODE_LENGTH))

        return code
    except Exception as ex:
        raise ValueError('Error al generar el codigo qr')


class HistoryCustomerModelSerializer(serializers.ModelSerializer):

    issued_by = CustomerInvitationSimpleSerializer()
    used_by = CustomerInvitationSimpleSerializer()

    class Meta:
        model = HistoryCustomerInvitation
        fields = ('id', 'code', 'issued_by', 'used_by', 'date', 'is_pending')
        read_only_fields = fields


class CustomerPromotionModelSerializer(serializers.ModelSerializer):
    history = HistoryCustomerModelSerializer()

    class Meta:
        model = CustomerPromotion
        fields = ('id', 'name', 'description', 'history', 'customer', 'created_at',
                  'expiration_date', 'used', 'used_at')


