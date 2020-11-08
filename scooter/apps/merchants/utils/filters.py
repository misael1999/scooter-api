from django_filters.rest_framework import FilterSet, CharFilter, BooleanFilter

from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.merchants.models import Merchant


class MerchantFilter(FilterSet):

    class Meta:
        model = Merchant
        fields = ['category', 'subcategory', 'area', 'zone']

    def filter_by_ids(self, queryset, name, value):
        order_status_ids = value.strip().split(',')
        return queryset.filter(order_status_id__in=order_status_ids)


class MerchantDeliveryManFilter(FilterSet):
    status = CharFilter(method='filter_by_status_ids')

    class Meta:
        model = DeliveryMan
        fields = ['status']

    def filter_by_status_ids(self, queryset, name, value):
        status_ids = value.strip().split(',')
        return queryset.filter(status_id__in=status_ids)