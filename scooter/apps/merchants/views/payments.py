# Django rest
# Mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
# Permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from scooter.apps.common.models import Status
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant
# Models
from scooter.apps.merchants.models.payments import MerchantPaymentMethod
# Serializers
from scooter.apps.merchants.serializers.payments import (MerchantPaymentMethodModelSerializer,
                                                         MerchantPaymentMethodSimpleSerializer)
# Utilities
from scooter.utils.viewsets import ScooterViewSet


class MerchantPaymentMethodViewSet(ScooterViewSet, mixins.ListModelMixin,
                                   mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                                   mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """ Handle add payment methods """
    queryset = MerchantPaymentMethod.objects.all()
    serializer_class = MerchantPaymentMethodModelSerializer
    # filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    # search_fields = ('name',)
    # ordering_fields = ('name',)
    # filter_fields = ('status',)
    lookup_field = 'id'

    def get_permissions(self):
        permission_classes = []
        if self.action in ['create', 'update', 'destroy', 'perform_destroy']:
            permission_classes = [IsAuthenticated, IsAccountOwnerMerchant]
        if self.action in ['list']:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return MerchantPaymentMethodSimpleSerializer
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
