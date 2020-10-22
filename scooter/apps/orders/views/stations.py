""" Stations view set """
# Django rest framework
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
# Utilities
from scooter.apps.orders.utils.filters import OrderFilter
from scooter.utils.viewsets.scooter import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.orders.permissions import IsOrderStationOwner
from scooter.apps.stations.permissions import IsAccountOwnerStation
# Serializers
from scooter.apps.orders.serializers import (OrderModelSerializer,
                                             RejectOrderByDeliverySerializer,
                                             OrderWithDetailModelSerializer,
                                             RejectOrderStationSerializer, AssignDeliveryManStationSerializer,
                                             AcceptOrderMerchantSerializer, RejectOrderMerchantSerializer,
                                             CancelOrderMerchantSerializer)
# Models
from scooter.apps.orders.models.orders import Order
# Mixin
from scooter.apps.common.mixins import AddStationMixin
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import (DjangoFilterBackend)


class StationOrderViewSet(ScooterViewSet, AddStationMixin,
                          mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = OrderModelSerializer
    queryset = Order.objects.all()
    station = None
    permission_classes = (IsAuthenticated, IsAccountOwnerStation)
    lookup_field = 'pk'
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('customer__name', 'from_address__street', 'from_address__suburb', 'qr_code')
    ordering_fields = ('created', 'customer__name')
    # Affect the default order
    # ordering = ('-created', 'passengers__count')
    filter_class = OrderFilter

    def get_queryset(self):
        if self.action == 'list':
            return self.station.order_set.all()
        return self.queryset

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return OrderWithDetailModelSerializer
        return self.serializer_class

    def get_permissions(self):
        """Assign permission based on action."""
        permissions = [IsAuthenticated, IsAccountOwnerStation]
        if self.action in ['reject_order', 'assign_order', 'retrieve']:
            permissions.append(IsOrderStationOwner)
        return [p() for p in permissions]

    def get_object(self):
        obj = get_object_or_404(Order,
                                id=self.kwargs['pk'])
        return obj

    @action(methods=['put'], detail=True)
    def reject_order(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = RejectOrderByDeliverySerializer(
            order,
            data=request.data,
            context={'station': self.station, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Solicitud rechazada')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def assign_order(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = AssignDeliveryManStationSerializer(
            order,
            data=request.data,
            context={'station': self.station, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Pedido aceptado correctamente')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['PUT'], detail=True)
    def accept_order_merchant(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = AcceptOrderMerchantSerializer(
            order,
            data=request.data,
            context={'merchant': order.merchant, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Pedido aceptado correctamente')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['PUT'], detail=True)
    def reject_order_merchant(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = RejectOrderMerchantSerializer(
            order,
            data=request.data,
            context={'merchant': order.merchant, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Solicitud rechazada correctamente')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def cancel_order_merchant(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = CancelOrderMerchantSerializer(
            order,
            data=request.data,
            context={'merchant': order.merchant, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='El Pedido ha sido cancelado correctamente')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def reject_order(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = RejectOrderStationSerializer(
            order,
            data=request.data,
            context={'station': self.station, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Pedido rechazado correctamente')
        return Response(data=data, status=status.HTTP_200_OK)
