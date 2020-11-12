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
from scooter.apps.common.models import Status
from scooter.apps.stations.models import StationZone
# Serializers
from scooter.apps.stations.serializers import StationZoneSerializer
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Permissions
from scooter.apps.stations.permissions import IsAccountOwnerStation


class StationZoneViewSet(ScooterViewSet, mixins.ListModelMixin,
                         mixins.CreateModelMixin, mixins.UpdateModelMixin,
                         mixins.RetrieveModelMixin, AddStationMixin, mixins.DestroyModelMixin):
    """ Handle add zones """
    queryset = StationZone.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerStation)
    serializer_class = StationZoneSerializer
    lookup_field = 'id'
    station = None

    def perform_destroy(self, instance):
        try:
            sts = Status.objects.get(slug_name='inactive')
            instance.status = sts
            instance.save()
        except Status.DoesNotExist:
            error = self.set_error_response(status=False, field='status',
                                            message='Ha ocurrido un error al desactivar la zona')
            return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['PATCH'])
    def unlock(self, request, *args, **kwargs):
        zone = self.get_object()
        sts = Status.objects.get(slug_name='active')
        # Send instance of zone for validate of name not exist
        zone.status = sts
        zone.save()
        data = self.set_response(status=True, data={}, message="Zona activada correctamente")
        return Response(data=data, status=status.HTTP_200_OK)
    # def get_permissions(self):
    #     permission_classes = []
    #     if self.action in ['create', 'update', 'destroy', 'perform_destroy']:
    #         permission_classes = [IsAuthenticated, IsAccountOwnerStation]
    #     if self.action in ['list']:
    #         permission_classes = [IsAuthenticated]
    #
    #     return [permission() for permission in permission_classes]
