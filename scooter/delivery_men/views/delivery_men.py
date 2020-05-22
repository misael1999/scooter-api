# Django rest
from rest_framework import mixins, status
from rest_framework.response import Response
# Models
from scooter.delivery_men.models.delivery_men import DeliveryMen
# Serializers
from scooter.delivery_men.serializers.delivery_men import (CreateDeliveryMenSerializer,
                                                           DeliveryMenModelSerializer)
# Viewset
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.common.mixins.stations import AddStationMixin
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from scooter.users.permissions import IsAccountOwnerStation


class DeliveryMenStationViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin, mixins.CreateModelMixin,
                                mixins.ListModelMixin, AddStationMixin):
    """ View set for the stations can register a new delivery man """

    serializer_class = DeliveryMenModelSerializer
    queryset = DeliveryMen.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerStation)
    station = None

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active delivery men """
        if self.action == 'list':
            return self.station.deliverymen_set.filter(status__slug_name='active')

        return self.queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create':
            serializer_class = CreateDeliveryMenSerializer
        return serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data=DeliveryMenModelSerializer(obj).data,
                                 message='Se ha registrado un nuevo repartidor')
        return Response(data=data, status=status.HTTP_201_CREATED)
