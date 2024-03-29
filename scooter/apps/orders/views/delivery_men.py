""" Delivery man order view set """
# Django rest framework
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
# Utilities
from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.orders.models import Order
from scooter.apps.orders.utils.filters import OrderFilter
from scooter.utils.viewsets.scooter import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.orders.permissions import IsOrderDeliveryManStationOwner, IsOrderDeliveryManOwner
from scooter.apps.delivery_men.permissions import IsAccountOwnerDeliveryMan
# Serializers
from scooter.apps.orders.serializers import (OrderModelSerializer,
                                             RejectOrderByDeliverySerializer,
                                             AcceptOrderByDeliveryManSerializer,
                                             OrderWithDetailModelSerializer,
                                             ScanQrOrderSerializer, UpdateOrderStatusSerializer)
# Models
from scooter.apps.orders.models.orders import Order
# Mixin
from scooter.apps.common.mixins import AddDeliveryManMixin


class DeliveryMenOrderViewSet(ScooterViewSet, AddDeliveryManMixin,
                              mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = OrderModelSerializer
    queryset = Order.objects.all()
    delivery_man = None
    permission_classes = (IsAuthenticated, IsAccountOwnerDeliveryMan)
    lookup_field = 'pk'
    filter_class = OrderFilter

    """ Method dispatch in AddCustomerMixin """

    def get_queryset(self):
        if self.action == 'list':
            return Order.objects.filter(delivery_man=self.delivery_man)
        return self.queryset

    def get_permissions(self):
        """Assign permission based on action."""
        permissions = [IsAuthenticated, IsAccountOwnerDeliveryMan]
        if self.action in ['reject_order', 'accept_order', 'retrieve', 'is_owner']:
            permissions.append(IsOrderDeliveryManStationOwner)
        elif self.action in ['list', 'current_orders']:
            pass
        else:
            permissions.append(IsOrderDeliveryManOwner)
        return [p() for p in permissions]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return OrderWithDetailModelSerializer
        return self.serializer_class

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
            context={'delivery_man': self.delivery_man, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Solicitud rechazada')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def accept_order(self, request, *args, **kwargs):
        order = self.get_object()
        delivery_man = self.delivery_man
        serializer = AcceptOrderByDeliveryManSerializer(
            order,
            data=request.data,
            context={'delivery_man': delivery_man, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order_save = serializer.save()
        # # Check if the order is the owner delivery men
        # order_check = Order.objects.get(pk=order.id)
        # if order_check.delivery_man is not delivery_man:
        #     return Response(data=self.set_error_response(status=False, field="detail",
        #                                                  message="El pedido fue aceptagdo por otro repartidor"),
        #                     status=status.HTTP_400_BAD_REQUEST)

        data = self.set_response(status=True,
                                 data={},
                                 message='Solicitud aceptada')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'])
    def validate_qr(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = ScanQrOrderSerializer(
            order,
            data=request.data,
            context={'delivery_man': self.delivery_man, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='QR validado correctamente')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'])
    def update_status(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(
            order,
            data=request.data,
            context={'delivery_man': self.delivery_man, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Estatus actualizado correctamente')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def is_owner(self, request, *args, **kwargs):
        # Check if the order is the owner delivery men
        delivery_man = self.delivery_man
        order = self.get_object()
        is_owner = False
        if order.delivery_man_id is delivery_man.id:
            is_owner = True

        return Response(data={'is_owner': is_owner},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def current_orders(self, request, *args, **kwargs):
        #
        order_in_process = Order.objects.filter(delivery_man=self.delivery_man, in_process=True)
        order_await_confirmation = Order.objects.filter(station=self.delivery_man.station,
                                                        order_status__slug_name__in=['await_delivery_man'],
                                                        delivery_man=None)
        data = {
            'in_process': OrderWithDetailModelSerializer(order_in_process, many=True).data,
            'await_confirmation': OrderWithDetailModelSerializer(order_await_confirmation, many=True).data
        }
        return Response(data=data,
                        status=status.HTTP_200_OK)

    # @action(detail=True, methods=['PUT'], url_path="purchase/already_in_commerce")
    # def already_in_commerce(self, request, *args, **kwargs):
    #     order = self.get_object()
    #     serializer = AlreadyInCommerceSerializer(
    #         order,
    #         data=request.data,
    #         context={'delivery_man': self.delivery_man, 'order': order},
    #         partial=False
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     order = serializer.save()
    #     data = self.set_response(status=True,
    #                              data={},
    #                              message='Estatus cambiado correctamente')
    #     return Response(data=data, status=status.HTTP_200_OK)
    #
    # @action(detail=True, methods=['PUT'], url_path="purchase/already_here")
    # def already_here(self, request, *args, **kwargs):
    #     order = self.get_object()
    #     serializer = AlreadyHereSerializer(
    #         order,
    #         data=request.data,
    #         context={'delivery_man': self.delivery_man, 'order': order},
    #         partial=False
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     order = serializer.save()
    #     data = self.set_response(status=True,
    #                              data={},
    #                              message='Estatus cambiado correctamente')
    #     return Response(data=data, status=status.HTTP_200_OK)
    #
    # @action(detail=True, methods=['PUT'], url_path="purchase/on_way_commerce")
    # def on_way_commerce(self, request, *args, **kwargs):
    #     order = self.get_object()
    #     serializer = OnWayCommercePurchaseSerializer(
    #         order,
    #         data=request.data,
    #         context={'delivery_man': self.delivery_man, 'order': order},
    #         partial=False
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     order = serializer.save()
    #     data = self.set_response(status=True,
    #                              data={},
    #                              message='Estatus cambiado correctamente')
    #     return Response(data=data, status=status.HTTP_200_OK)
    #
    # @action(detail=True, methods=['PUT'], url_path="purchase/on_delivery_process")
    # def on_delivery_process(self, request, *args, **kwargs):
    #     order = self.get_object()
    #     serializer = OnDeliveryProcessPurchaseSerializer(
    #         order,
    #         data=request.data,
    #         context={'delivery_man': self.delivery_man, 'order': order},
    #         partial=False
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     order = serializer.save()
    #     data = self.set_response(status=True,
    #                              data={},
    #                              message='Estatus cambiado correctamente')
    #     return Response(data=data, status=status.HTTP_200_OK)
