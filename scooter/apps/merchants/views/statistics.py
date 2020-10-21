# Django rest
from django.contrib.gis.geos import Point
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

from scooter.apps.common.mixins import AddMerchantMixin
from scooter.apps.merchants.models import Merchant
# Permissions
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant, IsSameMerchant
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Models
# Serializers
from scooter.apps.merchants.serializers import (SummarySalesSerializer)

from scooter.apps.users.serializers.users import UserModelSimpleSerializer
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.db.models.functions import Distance


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
