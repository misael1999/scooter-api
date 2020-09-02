# Django rest
from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.response import Response
# Models
from scooter.apps.customers.models.customers import CustomerPromotion, HistoryCustomerInvitation

# Viewset
from scooter.apps.customers.serializers import (CustomerPromotionModelSerializer,
                                                HistoryCustomerModelSerializer)
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins.customers import AddCustomerMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.customers.permissions import IsAccountOwnerCustomer
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CustomerPromotionsViewSet(ScooterViewSet, mixins.ListModelMixin, AddCustomerMixin):
    """ View set for the customers can register a new address """

    serializer_class = CustomerPromotionModelSerializer
    queryset = CustomerPromotion.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerCustomer)
    # Filters
    filter_backends = (OrderingFilter,)
    # ordering_fields = ('created',)
    # Affect the default order
    ordering = ('-created',)

    """ Method dispatch in AddCustomerMixin """
    customer = None

    # def get_queryset(self):
    #     """ Personalized query when the action is a list so that it only returns active addresss """
    #     if self.action == 'list':
    #         return self.customer.customer.all()
    #     return self.queryset

    def list(self, request, *args, **kwargs):
        data = {}
        now = timezone.localtime(timezone.now())
        available_set = self.customer.customerpromotion_set.filter(expiration_date__gte=now, used=False)
        expiration_set = self.customer.customerpromotion_set.filter(Q(expiration_date__lte=now) | Q(used=True))
        pending_set = HistoryCustomerInvitation.objects.filter(used_by=self.customer)
        invitations_set = HistoryCustomerInvitation.objects.filter(issued_by=self.customer)
        data['history'] = HistoryCustomerModelSerializer(invitations_set, many=True).data
        data['pending'] = HistoryCustomerModelSerializer(pending_set, many=True).data
        data['available'] = CustomerPromotionModelSerializer(available_set, many=True).data
        data['expiration'] = CustomerPromotionModelSerializer(expiration_set, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)
