from django_filters.rest_framework import FilterSet, CharFilter
from scooter.apps.delivery_men.models import DeliveryMan


class StationDeliveryManFilter(FilterSet):
    status = CharFilter(method='filter_by_status_ids')

    class Meta:
        model = DeliveryMan
        fields = ['status']

    def filter_by_status_ids(self, queryset, name, value):
        status_ids = value.strip().split(',')
        return queryset.filter(status_id__in=status_ids)
