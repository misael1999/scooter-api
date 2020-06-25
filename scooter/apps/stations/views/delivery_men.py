# Django rest
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Models
from scooter.apps.delivery_men.models.delivery_men import DeliveryMan
# Serializers
from scooter.apps.stations.serializers.delivery_men import (CreateDeliveryManSerializer,
                                                            DeliveryManModelSerializer)
from scooter.apps.stations.serializers.delivery_men import GetDeliveryMenNearestSerializer
# Viewset
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins.stations import AddStationMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.stations.permissions import IsAccountOwnerStation


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
        if self.action in ['list', 'nearest']:
            return self.station.deliveryman_set.filter(status__slug_name='active')

        return self.queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create':
            serializer_class = CreateDeliveryManSerializer
        if self.action == 'nearest':
            serializer_class = GetDeliveryMenNearestSerializer
        return serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data=DeliveryManModelSerializer(obj).data,
                                 message='Se ha registrado un nuevo repartidor')
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    def nearest(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data=DeliveryManModelSerializer(obj, many=True).data,
                                 message='Listado de repartidores mas cercanos')
        return Response(data=data, status=status.HTTP_200_OK)
