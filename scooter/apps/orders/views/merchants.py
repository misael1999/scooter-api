""" Merchants view set """
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
from scooter.apps.orders.permissions import IsOrderMerchantOwner
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant
# Serializers
from scooter.apps.orders.serializers import (OrderModelSerializer,
                                             OrderWithDetailModelSerializer,
                                             AcceptOrderMerchantSerializer,
                                             RejectOrderMerchantSerializer,
                                             CancelOrderMerchantSerializer,
                                             OrderReadyMerchantSerializer, OrderCurrentStatusSerializer)
from scooter.apps.orders.serializers.v2 import (OrderWithDetailModelSerializer,)
# Models
from scooter.apps.orders.models.orders import Order
# Mixin
from scooter.apps.common.mixins import AddMerchantMixin
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import (DjangoFilterBackend)


class MerchantOrderViewSet(ScooterViewSet, AddMerchantMixin,
                           mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = OrderModelSerializer
    queryset = Order.objects.all()
    merchant = None
    lookup_field = 'pk'
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('customer__name', 'from_address__street', 'from_address__suburb', 'qr_code')
    ordering_fields = ('created', 'customer__name')
    # Affect the default order
    # ordering = ('-created', 'passengers__count')
    filter_class = OrderFilter

    def get_queryset(self):
        if self.action == 'list':
            return self.merchant.order_set.all()
        return self.queryset

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return OrderWithDetailModelSerializer
        return self.serializer_class

    def get_permissions(self):
        """Assign permission based on action."""
        permissions = [IsAuthenticated, IsAccountOwnerMerchant]
        if self.action in ['reject_order', 'assign_order', 'retrieve']:
            permissions.append(IsOrderMerchantOwner)
        return [p() for p in permissions]

    def get_object(self):
        obj = get_object_or_404(Order,
                                id=self.kwargs['pk'])
        return obj

    @action(methods=['PUT'], detail=True)
    def accept_order(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = AcceptOrderMerchantSerializer(
            order,
            data=request.data,
            context={'merchant': self.merchant, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Pedido asignado correctamente')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['PUT'], detail=True)
    def reject_order(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = RejectOrderMerchantSerializer(
            order,
            data=request.data,
            context={'merchant': self.merchant, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Solicitud rechazada')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def current_status(self, request, *args, **kwargs):
        """ Get info the order status """
        order = self.get_object()
        data = self.set_response(status=True,
                                 data=OrderCurrentStatusSerializer(order).data,
                                 message='Estatus actual del pedido')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def cancel_order(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = CancelOrderMerchantSerializer(
            order,
            data=request.data,
            context={'merchant': self.merchant, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Pedido cancelado correctamente')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def order_ready(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = OrderReadyMerchantSerializer(
            order,
            data=request.data,
            context={'merchant': self.merchant, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Pedido listo')
        return Response(data=data, status=status.HTTP_200_OK)



