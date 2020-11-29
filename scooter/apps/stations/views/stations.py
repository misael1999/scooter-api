# Django rest
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

from scooter.apps.common.models import Area
from scooter.apps.common.serializers import AreaModelSerializer
from scooter.apps.users.permissions import IsAccountOwner
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Models
from scooter.apps.stations.models.stations import Station
# Serializers
from scooter.apps.stations.serializers import (StationSimpleModelSerializer,
                                               StationSignUpSerializer, StationUserModelSerializer,
                                               StationUpdateInfoSerializer, MembersStationModelSerializer,
                                               StationWithAllInfoSerializer)
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class StationViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.UpdateModelMixin):
    """ Handle signup and update of station """
    queryset = Station.objects.filter()
    serializer_class = StationUserModelSerializer
    pagination_class = None
    lookup_field = 'id'
    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('station_name',)
    ordering_fields = ('reputation',)
    ordering = ('-reputation', 'created')
    filter_fields = ('reputation',)

    def get_queryset(self):
        if self.action == 'list':
            return Station.objects.filter(status=1, information_is_complete=True)
        return self.queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        data = self.set_response(status='ok',
                                 data=response.data,
                                 message='Listado de centrales')

        return Response(data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create':
            serializer_class = StationSignUpSerializer
        if self.action in ['list', 'retrieve']:
            serializer_class = StationWithAllInfoSerializer
        return serializer_class

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['partial_update', 'update', 'update_info']:
            permission_classes = [IsAuthenticated, IsAccountOwner]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """ Station sign up """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = self.set_response(status='ok',
                                 data={},
                                 message='Gracias por registrarse, en breve recibira un correo para confirmar su cuenta')
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            station = self.get_object()
            partial = request.method == 'PATCH'
            serializer = StationSimpleModelSerializer(station, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = StationUserModelSerializer(station).data
        except Station.DoesNotExist:
            return Response(
                self.set_error_response(status=False, field='Detail', message='El usuario no es una estación'))
        return Response(self.set_response(status='ok', data=data, message='Información actualizada correctamente'))

    @action(detail=True, methods=('PATCH', 'PUT'))
    def update_info(self, request, *args, **kwargs):
        try:
            station = self.get_object()
            partial = request.method == 'PATCH'
            serializer = StationUpdateInfoSerializer(station, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = StationUserModelSerializer(station).data
        except Station.DoesNotExist:
            return Response(
                self.set_error_response(status=False, field='Detail', message='No existe la central'))
        return Response(self.set_response(status='ok', data=data, message='Información actualizada correctamente'))

    @action(detail=True, methods=['GET'])
    def clients(self, request, *args, **kwargs):
        try:
            station = self.get_object()
            queryset = station.memberstation_set.all()
            data = self.get_queryset_pagination(queryset=queryset,
                                                serialize_class=MembersStationModelSerializer)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(
                self.set_error_response(status=False, field='Detail', message='Error al consultar los clientes'))

    @action(detail=True, methods=['GET'])
    def area(self, request, *args, **kwargs):
        try:
            station = self.get_object()
            area = station.area
            data = AreaModelSerializer(area).data
            return Response(data, status=status.HTTP_200_OK)
        except Area.DoesNotExist:
            return Response(
                self.set_error_response(status=False, field='Detail', message='No existe el área'))
        except Exception as ex:
            return Response(
                self.set_error_response(status=False, field='Detail', message='Error al consultar el area'))