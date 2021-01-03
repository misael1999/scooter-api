# Django rest
from rest_framework.response import Response
# Mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from scooter.apps.common.mixins import AddCustomerMixin, AddSupportMixin
# Permissions
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from scooter.apps.customers.permissions import IsAccountOwnerCustomer
# Utilities
from scooter.apps.support.serializers import (SupportModelSimpleSerializer,
                                              CreateSupportModelSerializer)
from scooter.utils.viewsets import ScooterViewSet


class CustomerSupportViewSet(ScooterViewSet, mixins.ListModelMixin,
                             mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                             AddCustomerMixin):
    """ Handler support open """
    permission_classes = (IsAuthenticated, IsAccountOwnerCustomer)
    serializer_class = SupportModelSimpleSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering = ('-created',)
    filter_fields = ('status',)
    lookup_field = 'id'
    customer = None

    def get_queryset(self):
        if self.action in ['list', 'update', 'partial_update', 'retrieve']:
            return self.customer.support_set.all()
        return self.queryset

    def get_serializer_context(self):
        """ Add station to serializer context """
        context = super(CustomerSupportViewSet, self).get_serializer_context()
        context['is_customer'] = True
        return context

    def create(self, request, *args, **kwargs):
        serializer = CreateSupportModelSerializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        support = serializer.save()

        return Response(data=support, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action in ['create']:
            return CreateSupportModelSerializer
        return self.serializer_class
