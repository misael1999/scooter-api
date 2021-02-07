# Django rest
from rest_framework import status
from rest_framework.decorators import action
# Permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from scooter.apps.common.mixins import AddMerchantMixin
from scooter.apps.merchants.models import Merchant
# Models
# Serializers
from scooter.apps.merchants.serializers import (SummarySalesSerializer)
# Permissions
# Utilities
from scooter.utils.viewsets import ScooterViewSet


# Filters


class MerchantStatisticsViewSet(ScooterViewSet, AddMerchantMixin):
    """ Handle signup and update of merchant """
    permission_classes = (IsAuthenticated,)
    queryset = Merchant.objects.all()
    merchant = None

    @action(detail=False, methods=('GET', ))
    def summary(self, request, *args, **kwargs):
        serializer = SummarySalesSerializer(self.merchant, data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data=data, status=status.HTTP_200_OK)
