# Django rest
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Models
from scooter.apps.delivery_men.models.delivery_men import DeliveryMan
# Serializers
from scooter.apps.delivery_men.serializers.delivery_men import (CreateDeliveryManSerializer,
                                                                DeliveryManModelSerializer,
                                                                UpdateLocationDeliverySerializer)
# Viewset
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins.stations import AddStationMixin
from scooter.apps.common.mixins.delivery_men import AddDeliveryManMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.stations.permissions import IsAccountOwnerStation
from scooter.apps.delivery_men.permissions import IsAccountOwnerDeliveryMan


class DeliveryMenViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin):

    serializer_class = DeliveryManModelSerializer
    queryset = DeliveryMan.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerDeliveryMan)

    @action(detail=True, methods=('PATCH', ))
    def update_location(self, request,  *args, **kwargs):
        delivery_man = self.get_object()
        partial = request.method == 'PATCH'
        serializer = UpdateLocationDeliverySerializer(delivery_man, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.set_response(status='ok', data={},
                                          message='Ubicación actualizada correctamente'))


class DeliveryMenStationViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin, mixins.CreateModelMixin,
                                mixins.ListModelMixin, AddStationMixin):
    """ View set for the stations can register a new delivery man """

    serializer_class = DeliveryManModelSerializer
    queryset = DeliveryMan.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerStation)
    station = None

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active delivery men """
        if self.action == 'list':
            return self.station.deliveryman_set.filter(status__slug_name='active')

        return self.queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create':
            serializer_class = CreateDeliveryManSerializer
        return serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data=DeliveryManModelSerializer(obj).data,
                                 message='Se ha registrado un nuevo repartidor')
        return Response(data=data, status=status.HTTP_201_CREATED)
