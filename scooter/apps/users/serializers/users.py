""" Users serializers """
# General
from datetime import timedelta
from django.utils import timezone
# Django
from django.conf import settings
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.users.models.users import User
# JWT
import jwt
# Functions
from scooter.utils.functions import send_mail_verification, generate_verification_token


class UserModelSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'is_verified', 'auth_facebook')


class AccountVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=300)

    def validate_token(self, data):
        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('El código de verificación ha expirado')
        except jwt.PyJWTError:
            raise serializers.ValidationError('El código de verificación es invaliido', code="code_expired")
        else:
            if payload['token_type'] != 'email_confirmation':
                raise serializers.ValidationError('El código de verificación es invaliido')
            self.context['payload'] = payload
            return data

    def create(self, data):
        payload = self.context['payload']
        user = User.objects.get(username=payload['email'])
        # Validate if the user has already been verified
        if user.is_verified:
            raise serializers.ValidationError({'detail': 'El usuario ya se encuentra verificado'},
                                              code='user_already_verified')

        user.is_verified = True
        user.save()
        return user


class ResendCodeAccountVerificationSerializer(serializers.Serializer):

    username = serializers.EmailField()

    def create(self, data):
        try:
            user = User.objects.get(username=data['username'])
            if user.is_verified:
                raise serializers.ValidationError({'detail': 'El usuario ya se encuentra verificado'})
            code = generate_verification_token(user=user,
                                               exp=timezone.now() + timedelta(minutes=15),
                                               token_type='email_confirmation')

            subject = 'Verifica tu cuenta para comenzar'
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
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No existe un usuario con ese correo'})
        return user


class RecoverPasswordSerializer(serializers.Serializer):
    username = serializers.EmailField()

    def create(self, data):
        try:
            user = User.objects.get(username=data['username'])

            if user.auth_facebook:
                raise serializers.ValidationError({'detail': 'No es posible recuperar'
                                                             ' la contraseña cuando inicio con facebook'})

            code = generate_verification_token(user=user,
                                               exp=timezone.now() + timedelta(minutes=15),
                                               token_type='recover_password')

            subject = 'Completa tu solicitud de restablecimiento de contraseña'
            data = {
                'user': user,
                'token': code,
                'url': settings.URL_SERVER_FRONTEND
            }
            send_email = send_mail_verification(subject=subject,
                                                to_user=user.username,
                                                path_template="emails/users/recover_password.html",
                                                data=data)
            if not send_email:
                raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar el correo'})
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No existe una cuenta con ese correo'})
        return user


class RecoverPasswordVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=300)
    password = serializers.CharField(max_length=60)

    def validate_token(self, data):
        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('El código de verificación ha expirado')
        except jwt.PyJWTError:
            raise serializers.ValidationError('El código de verificación es invaliido')
        else:
            if payload['token_type'] != 'recover_password':
                raise serializers.ValidationError('El código de verificación es invaliido')
            self.context['payload'] = payload
            return data

    def create(self, data):
        payload = self.context['payload']
        user = User.objects.get(username=payload['email'])
        user.set_password(data['password'])
        user.save()
        return user

