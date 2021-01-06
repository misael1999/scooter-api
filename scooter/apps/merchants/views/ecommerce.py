# Cache methods
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
# Django rest
from django.contrib.gis.geos import Point
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

from scooter.apps.common.models import CategoryMerchant, Area, Status
from scooter.apps.common.serializers import AreaModelSerializer
from scooter.apps.merchants.models import Merchant
# Permissions
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant, IsSameMerchant
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Models
# Serializers
from scooter.apps.merchants.serializers import (MerchantSignUpSerializer,
                                                MerchantWithAllInfoSerializer, UpdateInfoMerchantSerializer,
                                                AvailabilityMerchantSerializer, ChangePasswordMerchantSerializer,
                                                MerchantInfoSerializer)

from scooter.apps.users.serializers.users import UserModelSimpleSerializer
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.db.models.functions import Distance


class MerchantViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                      mixins.ListModelMixin):
    """ Handle signup and update of merchant """
    queryset = Merchant.objects.all()
    serializer_class = MerchantWithAllInfoSerializer
    lookup_field = 'id'
    # Filters
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('merchant_name',)
    ordering_fields = ('is_open', 'reputation', 'created')
    ordering = ('-is_open', 'created')
    filter_fields = ('category', 'subcategory', 'area', 'zone', 'status', 'information_is_complete', 'reputation')

    @action(detail=False, methods=['GET'])
    def search(self, request, *args, **kwargs):
        try:

            pass
        except Exception as ex:
            print(ex.__str__())
            data = self.set_error_response(status=False, field='detail',
                                           message='Ha ocurrido un error desconocido')
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)