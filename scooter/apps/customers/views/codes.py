# Django rest
from rest_framework import mixins, status
from rest_framework.response import Response
# Models
from scooter.apps.customers.models.customers import CustomerAddress, CustomerInvitation
from scooter.apps.common.models.status import Status
# Serializers
from scooter.apps.customers.serializers.addresses import (CustomerAddressModelSerializer,
                                                          CreateCustomerAddressSerializer)
# Viewset
from scooter.apps.orders.serializers import CustomerInvitationModelSerializer
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins.customers import AddCustomerMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.customers.permissions import IsAccountOwnerCustomer
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CustomerInvitationsViewSet(ScooterViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                                 mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                                 mixins.DestroyModelMixin, AddCustomerMixin):
    """ View set for the customers can register a new address """

    serializer_class = CustomerInvitationModelSerializer
    queryset = CustomerInvitation.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerCustomer)
    # Filters
    filter_backends = (OrderingFilter,)
    # ordering_fields = ('created',)
    # Affect the default order
    ordering = ('-created',)

    """ Method dispatch in AddCustomerMixin """
    customer = None
    address_instance = None

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active addresss """
        if self.action == 'list':
            return self.customer.customerinvitation_set.filter(status__slug_name='active')
        return self.queryset
