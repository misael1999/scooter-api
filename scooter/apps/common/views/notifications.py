# Django rest
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from scooter.utils.viewsets import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
# Models

# Serializers
from scooter.apps.common.serializers import (NotifyAllSerializer)


class NotificationViewSet(ScooterViewSet, mixins.CreateModelMixin):
    """ Return status"""
    serializer_class = NotifyAllSerializer
    permission_classes = (IsAuthenticated,)
