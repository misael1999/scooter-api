# Django rest
from datetime import timedelta

from django.utils import timezone
from rest_framework import mixins, status
# Models
# Serializers
from scooter.apps.orders.models import Order
from scooter.apps.orders.serializers import OrderWithDetailModelSerializer, OrderWithDetailSimpleSerializer
from scooter.apps.stations.serializers import MembersStationModelSerializer
# Viewset
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


class CustomerStationViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                             mixins.ListModelMixin, AddStationMixin):
    """ View set for the stations can register a new delivery man """

    serializer_class = MembersStationModelSerializer
    permission_classes = (IsAuthenticated, IsAccountOwnerStation)
    station = None
    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('customer__name', 'customer__phone_number')
    ordering_fields = ('total_orders', 'total_orders_cancelled', 'customer__reputation', 'customer__name', 'customer__phone_number')
    # Affect the default order
    ordering = ('-total_orders', '-created')
    filter_fields = ('total_orders',)

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active delivery men """
        return self.station.memberstation_set.all()

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        from_date = get_date_from_querystring(self.request, 'from_date', timezone.localtime(timezone.now()))
        to_date = get_date_from_querystring(self.request, 'to_date',
                                            timezone.localtime(timezone.now()) + timedelta(days=1))

        history_orders = Order.objects.filter(order_date__range=(from_date, to_date),
                                              order_status__slug_name='delivered',
                                              station=self.station,
                                              customer_id=response.data['customer']['id'])
        history_orders_rejected = Order.objects.filter(order_date__range=(from_date, to_date),
                                                       order_status__slug_name__in=['cancelled', 'rejected'],
                                                       station=self.station,
                                                       customer_id=response.data['customer']['id'])
        response.data['history_orders_delivered'] = OrderWithDetailSimpleSerializer(history_orders, many=True).data
        response.data['history_orders_rejected'] = OrderWithDetailSimpleSerializer(history_orders_rejected,
                                                                                   many=True).data
        return response
