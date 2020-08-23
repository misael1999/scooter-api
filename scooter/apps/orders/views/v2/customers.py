""" Customers view set """
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
from scooter.apps.customers.permissions.customers import IsAccountOwnerCustomer
# Serializers
from scooter.apps.orders.serializers import (OrderModelSerializer,
                                             CalculateServicePriceSerializer,
                                             OrderWithDetailModelSerializer, OrderCurrentStatusSerializer,
                                             UpdateOrderStatusSerializer)
from scooter.apps.orders.serializers.v2 import (CreateOrderSerializer,
                                                RantingOrderCustomerSerializer,
                                                RetryOrderSerializer)
# Models
from scooter.apps.orders.models.orders import Order
# Mixin
from scooter.apps.common.mixins import AddCustomerMixin
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import (DjangoFilterBackend)


class CustomerOrderV2ViewSet(ScooterViewSet, mixins.CreateModelMixin, AddCustomerMixin,
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
    filter_class = OrderFilter
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
        """Create a new order to return a custom response """
        serializer = CreateOrderSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data={'order_id': obj},
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

    @action(methods=['GET'], detail=True)
    def current_status(self, request, *args, **kwargs):
        """ Get info the order status """
        order = self.get_object()
        data = self.set_response(status=True,
                                 data=OrderCurrentStatusSerializer(order).data,
                                 message='Estatus actual del pedido')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def rating(self, request, *args, **kwargs):
        """ Rated order by customer """
        order = self.get_object()
        serializer = RantingOrderCustomerSerializer(
            data=request.data,
            context={'customer': self.customer, 'order': order},
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Se ha valorado la orden correctamente')
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'])
    def retry(self, request, *args, **kwargs):
        """ Retry order when is rejected or there are not delivery men """

        order = self.get_object()
        serializer = RetryOrderSerializer(
            order,
            data=request.data,
            context={'customer': self.customer, 'order': order},
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        data = self.set_response(status=True,
                                 data={'order_id': order},
                                 message='Se ha enviado el pedido nuevamente')
        return Response(data=data, status=status.HTTP_200_OK)
