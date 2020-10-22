from django_filters.rest_framework import FilterSet, CharFilter, BooleanFilter
from scooter.apps.orders.models import Order


class OrderFilter(FilterSet):
    order_status = CharFilter(method='filter_by_ids')
    in_process = BooleanFilter()

    class Meta:
        model = Order
        fields = ['order_status', 'in_process', 'is_order_to_merchant']

    def filter_by_ids(self, queryset, name, value):
        order_status_ids = value.strip().split(',')
        return queryset.filter(order_status_id__in=order_status_ids)
