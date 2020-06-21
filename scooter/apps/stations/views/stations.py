# Django rest
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from scooter.apps.users.permissions import IsAccountOwner
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Models
from scooter.apps.stations.models.stations import Station
# Serializers
from scooter.apps.stations.serializers.stations import (StationSimpleModelSerializer,
                                                        StationSignUpSerializer, StationUserModelSerializer,
                                                        StationUpdateInfoSerializer)
from scooter.apps.users.serializers.users import UserModelSimpleSerializer


class StationViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.UpdateModelMixin):
    """ Handle signup and update of station """
    queryset = Station.objects.filter(status=1, information_is_complete=True)
    serializer_class = StationUserModelSerializer
    lookup_field = 'id'

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create':
            serializer_class = StationSignUpSerializer
        if self.action == 'list':
            serializer_class = StationSimpleModelSerializer
        return serializer_class

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['partial_update', 'update', 'update_info']:
            permission_classes = [IsAuthenticated, IsAccountOwner]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        data = self.set_response(status='ok',
                                 data=StationSimpleModelSerializer(self.queryset, many=True).data,
                                 message='Gracias por registrarse, en breve recibira un correo para confirmar su cuenta')
        return Response(data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        """ Station sign up """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = self.set_response(status='ok',
                                 data=UserModelSimpleSerializer(user).data,
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