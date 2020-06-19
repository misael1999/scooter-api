# Django rest
from rest_framework import mixins, status
from rest_framework.response import Response
# Models
from scooter.apps.customers.models.customers import CustomerAddress
from scooter.apps.common.models.status import Status
# Serializers
from scooter.apps.customers.serializers.addresses import (CustomerAddressModelSerializer,
                                                          CreateCustomerAddressSerializer)
# Viewset
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins.customers import AddCustomerMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.customers.permissions import IsAccountOwnerCustomer
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CustomerAddressesViewSet(ScooterViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                               mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin, AddCustomerMixin):
    """ View set for the customers can register a new address """

    serializer_class = CustomerAddressModelSerializer
    queryset = CustomerAddress.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerCustomer)
    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('alias', 'street')
    # ordering_fields = ('created',)
    # Affect the default order
    # ordering = ('-created', 'passengers__count')
    filter_fields = ('type_address',)

    """ Method dispatch in AddCustomerMixin """
    customer = None
    address_instance = None

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active addresss """
        if self.action == 'list':
            return self.customer.customeraddress_set.filter(status__slug_name='active')
        return self.queryset

    def get_serializer_context(self):
        """ Add merchant to serializer context """
        context = super(CustomerAddressesViewSet, self).get_serializer_context()
        # Send instance of address for validate of name not exist
        context['address_instance'] = self.address_instance
        return context

    def create(self, request, *args, **kwargs):
        """ To return a custom response """
        serializer = CreateCustomerAddressSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data=CustomerAddressModelSerializer(obj).data,
                                 message='Se ha registrado un nuevo direccion')
        return Response(data=data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        address = self.get_object()
        # Send instance of address for validate of name not exist
        self.address_instance = address
        serializer = CreateCustomerAddressSerializer(address, data=request.data, partial=True,
                                                     context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        address = serializer.save()
        address_created = CustomerAddressModelSerializer(address).data
        data = self.set_response(status=True, data=address_created, message="Dirección actualizado correctamente")
        return Response(data=data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        try:
            sts = Status.objects.get(slug_name='deleted')
            instance.status_id = sts
            instance.save()
        except Status.DoesNotExist:
            error = self.set_error_response(status=False, field='status',
                                            message='Ha ocurrido un error al borrar la dirección')
            return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
