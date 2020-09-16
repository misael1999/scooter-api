""" Custom token serializers """
import json
from time import time

import jwt
from jwt import PyJWTError
from jwt.algorithms import RSAAlgorithm
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
# Utilities
from django.utils import timezone
# Models
from django.conf import settings

from scooter.apps.marketing.models import Marketer
from scooter.apps.marketing.serializers import MarketerUserSimpleSerializer
from scooter.apps.merchants.models import Merchant
from scooter.apps.merchants.serializers import MerchantUserSimpleSerializer
from scooter.apps.users.models import User
from scooter.apps.stations.models import Station
from scooter.apps.customers.models import Customer
from scooter.apps.delivery_men.models import DeliveryMan
# Serializers
from scooter.apps.customers.serializers.customers import CustomerUserModelSerializer, generate_code_to_share
from scooter.apps.stations.serializers.delivery_men import DeliveryManUserModelSerializer
from scooter.apps.stations.serializers.stations import StationUserModelSerializer
# Facebook
import facebook
# JWT
from rest_framework_simplejwt.tokens import RefreshToken
# Request https
import requests


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


class MerchantTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {'no_active_account': 'Usuario o contraseña incorrectos'}

    def validate(self, attrs):
        data = super().validate(attrs)
        try:
            merchant = self.user.merchant
        except Merchant.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No tienes permisos para iniciar sesión'})

        if not self.user.is_verified:
            raise serializers.ValidationError({'detail': 'Es necesario que verifique su correo electronico {email}'.
                                              format(email=self.user.username)})

        data['merchant'] = MerchantUserSimpleSerializer(merchant).data
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


class MarketerTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {'no_active_account': 'Usuario o contraseña incorrectos'}

    def validate(self, attrs):
        data = super().validate(attrs)
        # Users can validate their account two days later
        try:
            marketer = self.user.marketer
        except Marketer.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No tienes permisos para iniciar sesión'})

        # Check the maximum time to validate
        # if timezone.localtime(timezone.now()) > self.user.verification_deadline and not self.user.is_verified:
        #     raise serializers.ValidationError({'detail': 'Ha expirado su tiempo de verificación'})

        data['marketer'] = MarketerUserSimpleSerializer(marketer).data

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
        is_new_user = False
        user_info = data['user']
        customer = None
        try:
            user = User.objects.get(facebook_id=user_info.get('id'))
            customer = user.customer
            customer.picture_url = user_info.get('picture')['data']['url']
            customer.save()
        except User.DoesNotExist:
            try:
                user_exist = User.objects.filter(username=user_info.get('email', '')).exists()
                # Verify that no exist user with the same email
                if user_exist:
                    message = "No es posible iniciar sesión con facebook, ya se encuentra registrado en la aplicación "
                    raise ValueError(message)
                is_new_user = True
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
                code_share = generate_code_to_share()
                customer = Customer.objects.create(user=user,
                                                   code_share=code_share,
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
        response['is_new_user'] = is_new_user
        response['access'] = str(refresh.access_token)
        response['customer'] = CustomerUserModelSerializer(customer).data
        return response


class CustomerAppleAuthSerializer(serializers.Serializer):
    APPLE_PUBLIC_KEY_URL = "https://appleid.apple.com/auth/keys"
    APPLE_PUBLIC_KEY = None
    APPLE_KEY_CACHE_EXP = 60 * 60 * 24
    APPLE_LAST_KEY_FETCH = 0

    authorization_code = serializers.CharField(max_length=1000)
    given_name = serializers.CharField(max_length=400, required=False, allow_null=True, allow_blank=True)
    family_name = serializers.CharField(max_length=400, required=False, allow_null=True, allow_blank=True)

    def validate(self, valid_data):
        try:
            # Get apple info
            # data = {
            #     'client_id': settings.AUTH_APPLE_ID_CLIENT,
            #     'client_secret': self.generate_key_secret(),
            #     'grant_type': 'authorization_code',
            #     'code': valid_data['authorization_code']
            # }
            #
            # headers = {"Content-Type": 'application/x-www-form-urlencoded'}
            #
            # req = requests.post(url='https://appleid.apple.com/auth/token', data=data, headers=headers)
            # if req.status_code >= 400:
            #     print(req.json())
            #     raise ValueError('Error al iniciar sesión')
            # json_obj = req.json()
            # decode = self._decode_apple_user_token(json_obj['id_token'])
            decode = self._decode_apple_user_token(valid_data['authorization_code'])
            valid_data['apple_id'] = decode['sub']
            valid_data['email'] = decode['email']
        except ValueError as e:
            print(e.args.__str__())
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al iniciar sesión con apple'})
        return valid_data

    def create(self, data):
        # is_new_user = False
        user_info = data
        customer = None
        try:
            user = User.objects.get(apple_id=user_info.get('apple_id'))
            customer = user.customer
        except User.DoesNotExist:
            try:
                user_exist = User.objects.filter(username=user_info.get('email', '')).exists()
                # Verify that no exist user with the same email
                if user_exist:
                    message = "No es posible iniciar sesión con apple, ya se encuentra registrado en la aplicación "
                    raise ValueError(message)
                # Generate password random
                password = User.objects.make_random_password()
                user = User(
                    username=user_info.get('email', 'sin email'),
                    apple_id=user_info.get('apple_id'),
                    auth_facebook=False,
                    is_client=True,
                    verification_deadline=timezone.localtime(timezone.now()),
                    is_verified=True)
                user.set_password(password)
                user.save()
                # Create customer
                code_share = generate_code_to_share()
                give_name = data.get('given_name', None)
                family_name = data.get('family_name', '')
                full_name = 'Usuario anónimo apple'
                if give_name:
                    full_name = give_name + family_name

                customer = Customer.objects.create(user=user,
                                                   name=full_name,
                                                   code_share=code_share)

            except ValueError as ex:
                raise serializers.ValidationError({'detail': str(ex)})
            except Exception as ex:
                print(ex.__str__())
                print('Error in auth apple please check it')
                raise serializers.ValidationError({"detail": 'Ha ocurrido un error desconocido'})

        # Generate token
        refresh = RefreshToken.for_user(user)
        response = dict()
        response['refresh'] = str(refresh)
        response['access'] = str(refresh.access_token)
        response['customer'] = CustomerUserModelSerializer(customer).data
        return response

    def _fetch_apple_public_key(self):
        # Check to see if the public key is unset or is stale before returning

        key_payload = requests.get(self.APPLE_PUBLIC_KEY_URL).json()
        APPLE_PUBLIC_KEY = RSAAlgorithm.from_jwk(json.dumps(key_payload["keys"][0]))
        return APPLE_PUBLIC_KEY

    def _decode_apple_user_token(self, apple_user_token):
        public_key = self._fetch_apple_public_key()
        try:
            token = jwt.decode(apple_user_token, public_key, audience=settings.AUTH_APPLE_ID_CLIENT, algorithm="RS256")
        except jwt.exceptions.ExpiredSignatureError as e:
            raise Exception("That token has expired")
        except jwt.exceptions.InvalidAudienceError as e:
            raise Exception("That token's audience did not match")
        except Exception as e:
            print(e)
            raise Exception("An unexpected error occoured")

        return token

    def retrieve_user(self, user_token):
        token = self._decode_apple_user_token(user_token)
        # apple_user =
        return token

    def generate_key_secret(self):
        now = int(time())
        client_id = settings.AUTH_APPLE_ID_CLIENT
        team_id = settings.AUTH_APPLE_ID_TEAM
        key_id = settings.AUTH_APPLE_ID_KEY
        private_key = settings.AUTH_APPLE_ID_SECRET
        TOKEN_AUDIENCE = 'https://appleid.apple.com'
        TOKEN_TTL_SEC = 3600 * 60

        headers = {'kid': key_id}
        payload = {
            'iss': team_id,
            'iat': now,
            'exp': now + TOKEN_TTL_SEC,
            'aud': TOKEN_AUDIENCE,
            'sub': client_id,
        }

        return jwt.encode(payload, key=private_key, algorithm='ES256',
                          headers=headers)
