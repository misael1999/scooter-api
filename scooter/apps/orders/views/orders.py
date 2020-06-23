# Django rest framework
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
# Utilities
from scooter.utils.viewsets.scooter import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.customers.permissions.customers import IsAccountOwnerCustomer
from scooter.apps.delivery_men.permissions import IsAccountOwnerDeliveryMan
# Serializers
from scooter.apps.orders.serializers.orders import (OrderModelSerializer,
                                                    CreateOrderSerializer,
                                                    CalculateServicePriceSerializer,
                                                    RejectOrderByDeliverySerializer,
                                                    AcceptOrderByDeliveryManSerializer,
                                                    OrderWithDetailModelSerializer)
# Models
from scooter.apps.orders.models.orders import Order
from scooter.apps.delivery_men.models import DeliveryMan
# Mixin
from scooter.apps.common.mixins import AddCustomerMixin, AddDeliveryManMixin


class CustomerOrderViewSet(ScooterViewSet, mixins.CreateModelMixin, AddCustomerMixin,
                           mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderModelSerializer
    permission_classes = (IsAuthenticated, IsAccountOwnerCustomer)
    customer = None

    """ Method dispatch in AddCustomerMixin """

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return OrderWithDetailModelSerializer
        return self.serializer_class

    def get_queryset(self):
        if self.action == 'list':
            return self.customer.order_set.all()

        return self.queryset

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


class DeliveryMenOrderViewSet(ScooterViewSet, AddDeliveryManMixin,
                              mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = OrderModelSerializer
    queryset = Order.objects.all()
    delivery_man = None
    permission_classes = (IsAuthenticated, IsAccountOwnerDeliveryMan)
    lookup_field = 'pk'

    def get_queryset(self):
        if self.action == 'list':
            return Order.objects.filter(delivery_man=self.delivery_man)
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderWithDetailModelSerializer
        return self.serializer_class

    def get_object(self):
        return self.queryset.get(id=self.kwargs['pk'])

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
