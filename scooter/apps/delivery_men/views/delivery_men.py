# Django rest
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Models
from scooter.apps.delivery_men.models.delivery_men import DeliveryMan
# Serializers
from scooter.apps.delivery_men.serializers.delivery_men import (DeliveryManModelSerializer,
                                                                UpdateLocationDeliverySerializer,
                                                                AvailabilityDeliverySerializer)
# Viewset
from scooter.utils.viewsets.scooter import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.delivery_men.permissions import IsAccountOwnerDeliveryMan


class DeliveryMenViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin):
    serializer_class = DeliveryManModelSerializer
    queryset = DeliveryMan.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerDeliveryMan)

    @action(detail=True, methods=('PATCH',))
    def update_location(self, request, *args, **kwargs):
        delivery_man = self.get_object()
        partial = request.method == 'PATCH'
        serializer = UpdateLocationDeliverySerializer(delivery_man, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.set_response(status='ok', data={},
                                          message='Ubicación actualizada correctamente'))

    @action(detail=True, methods=('PATCH',))
    def update_availability(self, request, *args, **kwargs):
        delivery_man = self.get_object()
        partial = request.method == 'PATCH'
        serializer = AvailabilityDeliverySerializer(delivery_man, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.set_response(status='ok', data={},
                                          message='Cambio de disponibilidad correctamente'))
