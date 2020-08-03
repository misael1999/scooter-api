# Django rest
from rest_framework import mixins, status
from scooter.utils.viewsets import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
# Models

# Serializers
from scooter.apps.common.serializers import (NotifyAllCustomersSerializer,)


class NotificationViewSet(ScooterViewSet, mixins.CreateModelMixin ):
    """ Return status"""
    serializer_class = NotifyAllCustomersSerializer
    permission_classes = (IsAuthenticated,)
