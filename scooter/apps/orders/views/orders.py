""" Station, customer, delivery man for order view """
# Django rest framework
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
# Utilities
from scooter.utils.viewsets.scooter import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.orders.permissions import IsOrderStationOwner, IsOrderDeliveryManOwner
from scooter.apps.customers.permissions.customers import IsAccountOwnerCustomer
from scooter.apps.delivery_men.permissions import IsAccountOwnerDeliveryMan
from scooter.apps.stations.permissions import IsAccountOwnerStation
# Serializers
from scooter.apps.orders.serializers import (OrderModelSerializer,
                                             CreateOrderSerializer,
                                             CalculateServicePriceSerializer,
                                             RejectOrderByDeliverySerializer,
                                             AcceptOrderByDeliveryManSerializer,
                                             OrderWithDetailModelSerializer,
                                             RejectOrderStationSerializer, AssignDeliveryManStationSerializer)
# Models
from scooter.apps.orders.models.orders import Order
from scooter.apps.delivery_men.models import DeliveryMan
# Mixin
from scooter.apps.common.mixins import AddCustomerMixin, AddDeliveryManMixin, AddStationMixin
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
""" Customer view set """


class CustomerOrderViewSet(ScooterViewSet, mixins.CreateModelMixin, AddCustomerMixin,
                           mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderModelSerializer
    permission_classes = (IsAuthenticated, IsAccountOwnerCustomer)
    customer = None
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('customer__name', 'from_address__street', 'from_address__suburb', 'qr_code')
    ordering_fields = ('created', 'customer__name')
    # Affect the default order
    # ordering = ('-created', 'passengers__count')
    filter_fields = ('order_status',)
    """ Method dispatch in AddCustomerMixin """

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return OrderWithDetailModelSerializer
        return self.serializer_class

    def get_queryset(self):
        if self.action == 'list':
            return self.customer.order_set.all()

        return self.queryset

    def get_object(self):
        obj = get_object_or_404(Order,
                                id=self.kwargs['pk'])
        return obj

    def create(self, request, *args, **kwargs):
        """Create a new order
        To return a custom response """
        serializer = CreateOrderSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Solicitud de servicio enviada')
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def service_price(self, request, *args, **kwargs):
        """ Calculate price of the servive before request the service """
        serializer = CalculateServicePriceSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data={'price_service': obj},
                                 message='Precio del servicio')
        return Response(data=data, status=status.HTTP_200_OK)


""" Delivery man view set """


class DeliveryMenOrderViewSet(ScooterViewSet, AddDeliveryManMixin,
                              mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = OrderModelSerializer
    queryset = Order.objects.all()
    delivery_man = None
    permission_classes = (IsAuthenticated, IsAccountOwnerDeliveryMan)
    lookup_field = 'pk'

    """ Method dispatch in AddCustomerMixin """

    def get_queryset(self):
        if self.action == 'list':
            return Order.objects.filter(delivery_man=self.delivery_man)
        return self.queryset

    def get_permissions(self):
        """Assign permission based on action."""
        permissions = [IsAuthenticated, IsAccountOwnerDeliveryMan]
        if self.action in ['reject_order', 'accept_order', 'retrieve']:
            permissions.append(IsOrderDeliveryManOwner)
        return [p() for p in permissions]

    def get_serializer_class(self):
        if self.action == 'retrieve':
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
        serializer = AcceptOrderByDeliveryManSerializer(
            order,
            data=request.data,
            context={'delivery_man': self.delivery_man, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Solicitud aceptada')
        return Response(data=data, status=status.HTTP_200_OK)


""" Stations view set """


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
    filter_fields = ('order_status',)

    def get_queryset(self):
        if self.action == 'list':
            return Order.objects.filter(station=self.station)
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
                                 message='Pedido asignado correctamente')
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
