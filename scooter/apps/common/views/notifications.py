# Django rest
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from scooter.utils.viewsets import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
# Models

# Serializers
from scooter.apps.common.serializers import (NotifyAllCustomersSerializer, NotifyAllMerchantsSerializer)


class NotificationViewSet(ScooterViewSet, mixins.CreateModelMixin ):
    """ Return status"""
    serializer_class = NotifyAllCustomersSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['POST'])
    def merchants(self, request, *args, **kwargs):
        serializer = NotifyAllMerchantsSerializer(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={'message': 'Notificación envíada correctamente'}, status=status.HTTP_200_OK)
