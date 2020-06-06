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
                                                    CreateOrderSerializer)
# Mixin
from scooter.apps.common.mixins.customers import AddCustomerMixin


class CustomerOrderViewSet(ScooterViewSet, mixins.CreateModelMixin, AddCustomerMixin,
                           mixins.RetrieveModelMixin, mixins.ListModelMixin):

    serializer_class = OrderModelSerializer
    permission_classes = (IsAuthenticated, IsAccountOwnerCustomer)
    customer = None

    """ Method dispatch in AddCustomerMixin """

    def create(self, request, *args, **kwargs):
        """ To return a custom response """
        serializer = CreateOrderSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data=OrderModelSerializer(obj).data,
                                 message='Solicitud de servicio enviada')
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def service_price(self, request, *args, **kwargs):
        pass
