# Django rest
from rest_framework import mixins, status
from rest_framework.response import Response
# Models
from scooter.apps.stations.models.vehicles import Vehicle
from scooter.apps.common.models.status import Status
# Serializers
from scooter.apps.stations.serializers.vehicles import VehicleModelSerializer
# Viewset
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins.stations import AddStationMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.stations.permissions import IsAccountOwnerStation
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class VehiclesViewSet(ScooterViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin, AddStationMixin):

    """ View set for the stations can register a new vehicle """

    serializer_class = VehicleModelSerializer
    queryset = Vehicle.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerStation)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('plate', 'model', 'alias')
    ordering_fields = ('plate', 'model', 'year', 'alias')
    # Affect the default order
    ordering = ('-id', '-created')
    filter_fields = ('plate',)
    """ Method dispatch in AddStationMixin """
    station = None
    vehicle_instance = None

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active vehicles """
        if self.action == 'list':
            return self.station.vehicle_set.filter(status__slug_name='active')
        return self.queryset

    def get_serializer_context(self):
        """ Add merchant to serializer context """
        context = super(VehiclesViewSet, self).get_serializer_context()
        # Send instance of vehicle for validate of name not exist
        context['vehicle_instance'] = self.vehicle_instance
        return context

    def create(self, request, *args, **kwargs):
        """ To return a custom response """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data=VehicleModelSerializer(obj).data,
                                 message='Se ha registrado un nuevo vehiculo')
        return Response(data=data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        vehicle = self.get_object()
        # Send instance of vehicle for validate of name not exist
        self.vehicle_instance = vehicle
        serializer = self.get_serializer(vehicle, data=request.data, partial=True,
                                         context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.save()
        vehicle_created = VehicleModelSerializer(vehicle).data
        data = self.set_response(status=True, data=vehicle_created, message="Vehiculo actualizado correctamente")
        return Response(data=data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        try:
            sts = Status.objects.get(slug_name='deleted')
            instance.status_id = sts
            instance.save()
        except Status.DoesNotExist:
            error = self.set_error_response(status=False, field='status',
                                            message='Ha ocurrido un error al borrar el vehiculo')
            return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

