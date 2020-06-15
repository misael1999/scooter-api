# Django rest framework
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
# Utilities
from scooter.utils.viewsets.scooter import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.customers.permissions.customers import IsAccountOwnerCustomer
# Serializers
from scooter.apps.orders.serializers.orders import (OrderModelSerializer,
                                                    CreateOrderSerializer,
                                                    CalculateServicePriceSerializer)
# Models
from scooter.apps.orders.models.orders import Order
# Mixin
from scooter.apps.common.mixins import AddCustomerMixin, AddDeliveryManMixin


class CustomerOrderViewSet(ScooterViewSet, mixins.CreateModelMixin, AddCustomerMixin,
                           mixins.RetrieveModelMixin, mixins.ListModelMixin):

    queryset = Order.objects.all()
    serializer_class = OrderModelSerializer
    permission_classes = (IsAuthenticated, IsAccountOwnerCustomer)
    customer = None

    """ Method dispatch in AddCustomerMixin """

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

    queryset = Order.objects.all()
    serializer_class = OrderModelSerializer
    delivery_man = None

    def get_queryset(self):
        if self.action == 'list':
            return self.delivery_man.order_set.all()
        return self.queryset

    @action(methods=['put'], detail=True)
    def reject_order(self):

        pass
