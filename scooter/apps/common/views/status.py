# Django rest
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
# Custom viewset
from scooter.utils.viewsets import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
# Models
from scooter.apps.common.models.status import Status
from scooter.apps.common.models.common import Schedule, Service
from scooter.apps.common.models.orders import OrderStatus
# Serializers
from scooter.apps.common.serializers import (StatusModelSerializer,
                                             OrderStatusModelSerializer,
                                             ScheduleModelSerializer, ServiceModelSerializer)


class StatusViewSet(ScooterViewSet):
    """ Return status"""
    lookup_field = 'id'
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False, url_path="status")
    def status(self, request, *args, **kwargs):
        query = Status.objects.all()
        general_status = StatusModelSerializer(query, many=True).data
        data = self.set_response(status='ok', data=general_status, message='Estatus generales')
        return Response(data=data, status=status.HTTP_200_OK)    \


    @action(methods=['get'], detail=False)
    def order_status(self, request, *args, **kwargs):
        query = OrderStatus.objects.all()
        order_status = OrderStatusModelSerializer(query, many=True).data
        data = self.set_response(status='ok', data=order_status, message='Estatus de ordenes')
        return Response(data=data, status=status.HTTP_200_OK)    \


    @action(methods=['get'], detail=False)
    def schedules(self, request, *args, **kwargs):
        query = Schedule.objects.all()
        schedules = ScheduleModelSerializer(query, many=True).data
        data = self.set_response(status='ok', data=schedules, message='Horarios disponibles')
        return Response(data=data, status=status.HTTP_200_OK)    \


    @action(methods=['get'], detail=False)
    def services(self, request, *args, **kwargs):
        query = Service.objects.all()
        services = ServiceModelSerializer(query, many=True).data
        data = self.set_response(status='ok', data=services, message='Servicios disponibles')
        return Response(data=data, status=status.HTTP_200_OK)



