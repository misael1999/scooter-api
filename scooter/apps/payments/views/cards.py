# Django rest
from rest_framework.response import Response
# Mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from scooter.apps.common.mixins import AddCustomerMixin
# Permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from scooter.apps.customers.permissions import IsAccountOwnerCustomer
from scooter.apps.common.models import Status
# Models
from scooter.apps.payments.models.cards import Card
# Serializers
from scooter.apps.payments.serializers import CardModelSerializer, CardSimpleSerializer
# Utilities
from scooter.utils.viewsets import ScooterViewSet


class CardsViewSet(ScooterViewSet, mixins.ListModelMixin,
                   mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin, AddCustomerMixin):
    """ Handle add brands """
    queryset = Card.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerCustomer)
    serializer_class = CardModelSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('status',)
    lookup_field = 'id'
    customer = None

    # def get_permissions(self):
    #     permission_classes = []
    #     if self.action in ['create', 'update', 'destroy', 'perform_destroy']:
    #         permission_classes = [IsAuthenticated, IsSuperAdmin]
    #     if self.action in ['list']:
    #         permission_classes = [AllowAny]
    #
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action in ['list', 'update', 'partial_update', 'retrieve']:
            return Card.objects.filter(customer_id=self.customer.id)
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return CardSimpleSerializer
        return self.serializer_class

    def perform_destroy(self, instance):
        try:
            sts = Status.objects.get(slug_name='inactive')
            instance.status = sts
            instance.save()
        except Status.DoesNotExist:
            error = self.set_error_response(status=False, field='status',
                                            message='Ha ocurrido un error al borrar la categoria')
            return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
