# Django rest
from datetime import timedelta

from django.utils import timezone
from rest_framework import mixins, status
# Models
# Serializers
from rest_framework.response import Response

from scooter.apps.customers.models import CustomerPromotion
from scooter.apps.customers.serializers import CustomerPromotionModelSerializer
from scooter.apps.orders.models import Order
from scooter.apps.orders.serializers import OrderWithDetailModelSerializer, OrderWithDetailSimpleSerializer
from scooter.apps.stations.serializers import MembersStationModelSerializer
# Viewset
from scooter.apps.stations.serializers.promotions import CreateCustomerPromotionSerializer
from scooter.utils.functions import get_date_from_querystring
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins.stations import AddStationMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.stations.permissions import IsAccountOwnerStation
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class StationCustomerPromotionViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                                      mixins.ListModelMixin, mixins.CreateModelMixin,
                                      AddStationMixin):
    """ View set for the stations can register a new delivery man """

    serializer_class = CustomerPromotionModelSerializer
    queryset = CustomerPromotion.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerStation)
    station = None
    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name', 'customer__name', 'customer__phone_number')
    ordering_fields = ("expiration_date", "created_at", "customer__total_orders", "used", 'used_at')
    # Affect the default order
    ordering = ('-created', '-expiration_date', '-used', '-used_at')
    filter_fields = ('used', 'used_at')

    def create(self, request, *args, **kwargs):
        serializer = CreateCustomerPromotionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        data = self.set_response(status='ok',
                                 data={},
                                 message='Promociones creadas')
        return Response(data, status=status.HTTP_201_CREATED)
