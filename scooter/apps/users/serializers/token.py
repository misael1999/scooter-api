""" Custom token serializers """

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
# Utilities
from django.utils import timezone
# Models
from scooter.apps.users.models import User
from scooter.apps.stations.models import Station
from scooter.apps.customers.models import Customer
from scooter.apps.delivery_men.models import DeliveryMan
# Serializers
from scooter.apps.customers.serializers.customers import CustomerUserModelSerializer
from scooter.apps.stations.serializers.delivery_men import DeliveryManUserModelSerializer
from scooter.apps.stations.serializers.stations import StationUserModelSerializer
# Facebook
import facebook
# JWT
from rest_framework_simplejwt.tokens import RefreshToken


class StationTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {'no_active_account': 'Usuario o contraseña incorrectos'}

    def validate(self, attrs):
        data = super().validate(attrs)
        try:
            station = self.user.station
        except Station.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No tienes permisos para iniciar sesión'})

        if not self.user.is_verified:
            raise serializers.ValidationError({'detail': 'Es necesario que verifique su correo electronico {email}'.
                                              format(email=self.user.username)})

        data['station'] = StationUserModelSerializer(station).data
        # Add extra responses here
        # data['user'] = UserModelSerializer(self.user).data
        return data


class CustomerTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {'no_active_account': 'Usuario o contraseña incorrectos'}

    def validate(self, attrs):
        data = super().validate(attrs)
        # Users can validate their account two days later
        try:
            customer = self.user.customer
        except Customer.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No tienes permisos para iniciar sesión'})

        # Check the maximum time to validate
        # if timezone.localtime(timezone.now()) > self.user.verification_deadline and not self.user.is_verified:
        #     raise serializers.ValidationError({'detail': 'Ha expirado su tiempo de verificación'})
        if not self.user.is_verified:
            raise serializers.ValidationError({'detail': 'Es necesario que verifique su correo electronico {email}'.
                                              format(email=self.user.username)})

        data['customer'] = CustomerUserModelSerializer(customer).data

        # Add extra responses here
        # data['user'] = UserModelSerializer(self.user).data
        return data


class DeliveryManTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {'no_active_account': 'Télefono o contraseña incorrectos'}

    def validate(self, attrs):
        # Delivery man can validate their account
        data = super().validate(attrs)
        try:
            delivery_man = self.user.deliveryman
        except DeliveryMan.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No tienes permisos para iniciar sesión'})

        if delivery_man.status.slug_name == 'inactive':
            raise serializers.ValidationError({'detail': 'Te han dado de baja en tu central'})

        data['delivery_man'] = DeliveryManUserModelSerializer(delivery_man).data

        # Add extra responses here
        # data['user'] = UserModelSerializer(self.user).data
        return data


class CustomerFacebookAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=400)

    def validate(self, data):
        try:
            graph = facebook.GraphAPI(access_token=data['access_token'])
            user_info = graph.get_object(
                id='me',
                fields='first_name, middle_name, last_name, email, picture.type(large), id')
        except facebook.GraphAPIError:
            raise serializers.ValidationError({'detail': 'No es un usuario de facebook valido'})

        data['user'] = user_info
        return data

    def create(self, data):
        user_info = data['user']
        customer = None
        try:
            user = User.objects.get(facebook_id=user_info.get('id'))
            customer = user.customer
        except User.DoesNotExist:
            try:
                user_exist = User.objects.filter(username=user_info.get('email', '')).exists()
                # Verify that no exist user with the same email
                if user_exist:
                    message = "No es posible iniciar sesión con facebook, ya se encuentra registrado en la aplicación "
                    raise ValueError(message)

                # Generate password random
                password = User.objects.make_random_password()

                user = User(
                    username=user_info.get('email', '{0} sin email'.format(user_info.get('first_name'))),
                    facebook_id=user_info.get('id'),
                    auth_facebook=True,
                    is_client=True,
                    verification_deadline=timezone.localtime(timezone.now()),
                    is_verified=True)
                user.set_password(password)
                user.save()
                # Create customer
                first_name = user_info.get('first_name', '')
                middle_name = user_info.get('middle_name', '')
                last_name = user_info.get('last_name', '')
                full_name = '{first_name} {middle_name} {last_name}'.format(first_name=first_name,
                                                                            middle_name=middle_name,
                                                                            last_name=last_name)
                customer = Customer.objects.create(user=user,
                                                   picture_url=user_info.get('picture')['data']['url'],
                                                   name=full_name)
            except ValueError as ex:
                raise serializers.ValidationError({'detail': str(ex)})
            except Exception as ex:
                print(ex.__str__())
                print('Error in auth facebook please check it')
                raise serializers.ValidationError({"detail": 'Ha ocurrido un error desconocido'})

        # Generate token
        refresh = RefreshToken.for_user(user)
        response = dict()
        response['refresh'] = str(refresh)
        response['access'] = str(refresh.access_token)
        response['customer'] = CustomerUserModelSerializer(customer).data
        return response
