# Django rest
from django.db.models import Q
from rest_framework import mixins, status
from rest_framework.response import Response
# Models
from scooter.apps.customers.models.customers import CustomerInvitation, HistoryCustomerInvitation

# Viewset
from scooter.apps.customers.serializers import (CustomerInvitationModelSerializer,
                                                HistoryCustomerInvitationModelSerializer)
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins.customers import AddCustomerMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.customers.permissions import IsAccountOwnerCustomer
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CustomerInvitationsViewSet(ScooterViewSet, mixins.ListModelMixin, AddCustomerMixin):
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

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active addresss """
        if self.action == 'list':
            return self.customer.customerinvitation_set.filter()
        return self.queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs).data
        pendings = HistoryCustomerInvitation.objects.filter(Q(is_pending=True) |
                                                            Q(used_by=self.customer) |
                                                            Q(issued_by=self.customer))
        response['pendings'] = HistoryCustomerInvitationModelSerializer(pendings, many=True).data
        return Response(data=response, status=status.HTTP_200_OK)
