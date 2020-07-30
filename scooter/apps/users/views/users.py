# Django rest
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
# Mixins
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

from scooter.apps.common.models import AppVersion
from scooter.apps.users.permissions import IsAccountOwner
# Models
from scooter.apps.users.models.users import User
# Serializers
from scooter.apps.users.serializers.devices import DeleteDeviceSerializer
from scooter.apps.users.serializers.users import (UserModelSimpleSerializer,
                                                  TestNotificationSerializer,
                                                  RecoverPasswordSerializer,
                                                  RecoverPasswordVerificationSerializer,
                                                  AccountVerificationSerializer,
                                                  ResendCodeAccountVerificationSerializer, ContactSerializer,
                                                  AppVersionSerializer)
# Utilities
from scooter.utils.viewsets import ScooterViewSet


class UserViewSet(ScooterViewSet):
    """ Handle signup of merchant and client """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserModelSimpleSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['signup_client', 'signup_merchant', 'verify',
                           'forgot_password', 'recover_password', 'resend_code_verification']:
            permission_classes = [AllowAny]
        elif self.action in ['retrieve', 'client', 'merchant', 'test_notifications']:
            permission_classes = [IsAuthenticated, IsAccountOwner]
        elif self.action in ['contact', 'check_version']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], url_path="forgot-password")
    def forgot_password(self, request):
        """ Recover password request """
        serializer = RecoverPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'status': 'ok',
            'data': {},
            "message": "Se ha enviado un correo ha {email}".format(email=user.username)
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path="recover-password")
    def recover_password(self, request):
        """ Verification recover password request """
        serializer = RecoverPasswordVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'status': 'ok',
            'data': {},
            "message": "Se ha cambiado la contraseña para {email}".format(email=user.username)
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path="resend-code-verification")
    def resend_code_verification(self, request):
        """ Resend code to account verification """
        serializer = ResendCodeAccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'status': 'ok',
            'user': UserModelSimpleSerializer(user).data,
            "message": "Se ha cambiado un correo de verificación a {email}".format(email=user.username)
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path="verify")
    def verify(self, request):
        """ Verify user account (merchant and client) """
        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'status': 'ok',
            'user': UserModelSimpleSerializer(user).data,
            "message": "Se ha verificado correctamente"
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def test_notifications(self, request):
        """ Delete after testing """
        serializer = TestNotificationSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        notify = serializer.save()
        data = {
            'status': 'ok',
            'data': {},
            "message": "Se ha enviado la notificación"
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def send_notifications_delivery(self, request):
        """ Send all delivery men """
        serializer = TestNotificationSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        notify = serializer.save()
        data = {
            'status': 'ok',
            'data': {},
            "message": "Se ha enviado la notificación"
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def delete_devices(self, request, *args, **kwargs):
        """ Delete one device with token received """
        serializer = DeleteDeviceSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid()
        delete = serializer.save()
        data = {
            'status': 'ok',
            'data': {},
            "message": "Dispositivo eliminado correctamente"
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def contact(self, request, *args, **kwargs):
        """  """
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid()
        contact_true = serializer.save()
        data = {
            'status': 'ok',
            'data': {},
            "message": "Formulario enviado"
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    def check_version(self, request, *argsm, **kwargs):
        """ Last number version of app """
        version = AppVersion.objects.last()
        return Response(data=AppVersionSerializer(version).data, status=status.HTTP_200_OK)