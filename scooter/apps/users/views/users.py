# Django rest
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
# Mixins
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from scooter.apps.users.permissions import IsAccountOwner
# Models
from scooter.apps.users.models.users import User
# Serializers
from scooter.apps.users.serializers.users import (UserModelSimpleSerializer,
                                                  TestNotificationSerializer,
                                                  RecoverPasswordSerializer,
                                                  RecoverPasswordVerificationSerializer,
                                                  AccountVerificationSerializer,
                                                  ResendCodeAccountVerificationSerializer)
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
