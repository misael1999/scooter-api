from django_filters.rest_framework import FilterSet, CharFilter, BooleanFilter

from scooter.apps.merchants.models import Merchant


class MerchantFilter(FilterSet):

    class Meta:
        model = Merchant
        fields = ['category', 'subcategory', 'area', 'zone']

    def filter_by_ids(self, queryset, name, value):
        order_status_ids = value.strip().split(',')
        return queryset.filter(order_status_id__in=order_status_ids)
