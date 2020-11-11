# Django rest
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
# Mixins
from rest_framework import mixins
from scooter.apps.common.mixins import AddStationMixin
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

# Models
from scooter.apps.stations.models import StationZone
# Serializers
from scooter.apps.stations.serializers import StationZoneSerializer
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Permissions
from scooter.apps.stations.permissions import IsAccountOwnerStation


class StationZoneViewSet(ScooterViewSet, mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin, AddStationMixin):
    """ Handle add zones """
    queryset = StationZone.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerStation)
    serializer_class = StationZoneSerializer
    lookup_field = 'id'
    station = None

    # def get_permissions(self):
    #     permission_classes = []
    #     if self.action in ['create', 'update', 'destroy', 'perform_destroy']:
    #         permission_classes = [IsAuthenticated, IsAccountOwnerStation]
    #     if self.action in ['list']:
    #         permission_classes = [IsAuthenticated]
    #
    #     return [permission() for permission in permission_classes]
