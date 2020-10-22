# Django rest
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
# Custom viewset
from scooter.apps.orders.serializers import InvitedCalculateServicePriceSerializer
from scooter.utils.viewsets import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
# Models
from scooter.apps.common.models.status import Status
from scooter.apps.common.models.common import Schedule, Service, TypeAddress, TypeVehicle
from scooter.apps.common.models.orders import OrderStatus
# Serializers
from scooter.apps.common.serializers import (StatusModelSerializer,
                                             TypeVehicleSerializer,
                                             OrderStatusModelSerializer,
                                             NotifyAllSerializer,
                                             ScheduleModelSerializer, ServiceModelSerializer,
                                             TypeAddressModelSerializer)


class StatusViewSet(ScooterViewSet):
    """ Return status"""
    lookup_field = 'id'
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ['invited_service_price']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False, url_path="status")
    def status(self, request, *args, **kwargs):
        query = Status.objects.all()
        general_status = StatusModelSerializer(query, many=True).data
        data = self.set_response(status='ok', data=general_status, message='Estatus generales')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def order_status(self, request, *args, **kwargs):
        query = OrderStatus.objects.all()
        order_status = OrderStatusModelSerializer(query, many=True).data
        data = self.set_response(status='ok', data=order_status, message='Estatus de ordenes')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def schedules(self, request, *args, **kwargs):
        query = Schedule.objects.all()
        schedules = ScheduleModelSerializer(query, many=True).data
        data = self.set_response(status='ok', data=schedules, message='Horarios disponibles')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def services(self, request, *args, **kwargs):
        query = Service.objects.all()
        services = ServiceModelSerializer(query, many=True).data
        data = self.set_response(status='ok', data=services, message='Servicios disponibles')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def type_addresses(self, request, *args, **kwargs):
        query = TypeAddress.objects.all()
        type_addresses = TypeAddressModelSerializer(query, many=True).data
        data = self.set_response(status='ok', data=type_addresses, message='Tipos de direcciones')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def type_vehicles(self, request, *args, **kwargs):
        query = TypeVehicle.objects.all()
        type_addresses = TypeVehicleSerializer(query, many=True).data
        data = self.set_response(status='ok', data=type_addresses, message='Tipos de vehiculos')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def notifications(self, request, *args, **kwargs):
        serializer = NotifyAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = self.set_response(status='ok', data={}, message='Notificación enviada')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def invited_service_price(self, request, *args, **kwargs):
        """ Calculate price of the servive before request the service """
        serializer = InvitedCalculateServicePriceSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data={'price_service': obj},
                                 message='Precio del servicio')
        return Response(data=data, status=status.HTTP_200_OK)
