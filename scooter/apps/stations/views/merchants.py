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

from scooter.apps.common.models import Status
from scooter.apps.common.mixins import AddStationMixin
from scooter.apps.customers.permissions import IsStation
from scooter.apps.merchants.models import Merchant
# Permissions
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant, IsSameMerchant
# Utilities
from scooter.apps.stations.serializers import UpdateMerchantStationSerializer
from scooter.utils.viewsets import ScooterViewSet
# Models
# Serializers
from scooter.apps.merchants.serializers import (MerchantSignUpSerializer,
                                                MerchantWithAllInfoSerializer,
                                                AvailabilityMerchantSerializer,
                                                ChangePasswordMerchantSerializer,
                                                MerchantInfoSerializer)

from scooter.apps.users.serializers.users import UserModelSimpleSerializer
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.db.models.functions import Distance


class MerchantStationViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                             AddStationMixin,
                             mixins.CreateModelMixin, mixins.ListModelMixin,
                             mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """ Handle signup and update of merchant """
    queryset = Merchant.objects.all()
    permission_classes = (IsAuthenticated, IsStation)
    serializer_class = MerchantWithAllInfoSerializer
    lookup_field = 'id'
    # Filters
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('merchant_name',)
    ordering_fields = ('is_open', 'reputation', 'created')
    ordering = ('-is_open', 'created')
    filter_fields = ('category', 'subcategory', 'area', 'zone', 'status', 'information_is_complete', 'reputation')
    station = None

    # def get_queryset(self):
    #     if self.action == 'list':
    #         merchants = Merchant.objects.filter(status=1, information_is_complete=True)
    #         return merchants
    #     return self.queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create':
            serializer_class = MerchantSignUpSerializer
        if self.action in ['update', 'partial_update']:
            serializer_class = UpdateMerchantStationSerializer
        if self.action == 'retrieve':
            serializer_class = MerchantInfoSerializer
        if self.action in ['list']:
            serializer_class = MerchantWithAllInfoSerializer
        return serializer_class

    # def get_permissions(self):
    #     if self.action in ['list', 'retrieve', 'home']:
    #         permission_classes = [AllowAny]
    #     elif self.action in ['create']:
    #         permission_classes = [IsAuthenticated]
    #     elif self.action in ['partial_update', 'update', 'update_info']:
    #         permission_classes = [IsAuthenticated, IsSameMerchant]
    #     else:
    #         permission_classes = [IsAuthenticated]
    #
    #     return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """ Merchant sign up """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = self.set_response(status='ok',
                                 data={},
                                 message='Se ha registrado un nuevo comercio')
        return Response(data, status=status.HTTP_201_CREATED)

    # Cache requested url for each user for 2 hours
    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        return super(MerchantStationViewSet, self).retrieve(request, *args, **kwargs)

    @action(detail=True, methods=('PATCH',))
    def change_password(self, request, *args, **kwargs):
        customer = self.get_object()
        partial = request.method == 'PATCH'
        serializer = ChangePasswordMerchantSerializer(customer, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.set_response(status='ok', data={},
                                          message='Contraseña actualizada correctamente'))

    def perform_destroy(self, instance):
        try:
            sts = Status.objects.get(slug_name='inactive')
            instance.status = sts
            instance.save()
        except Status.DoesNotExist:
            error = self.set_error_response(status=False, field='status',
                                            message='Ha ocurrido un error al borrar el vehiculo')
            return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['PATCH', 'PUT'])
    def unlock(self, request, *args, **kwargs):
        merchant = self.get_object()
        sts = Status.objects.get(slug_name='active')
        # Send instance of vehicle for validate of name not exist
        merchant.status = sts
        merchant.save()
        data = self.set_response(status=True, data={}, message="Comercio desbloqueado correctamente")
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=True, methods=('PATCH', 'PUT'))
    def update_availability(self, request, *args, **kwargs):
        merchant = self.get_object()
        serializer = AvailabilityMerchantSerializer(merchant, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        status_availability = serializer.save()
        return Response(self.set_response(status='ok', data={'status': status_availability},
                                          message='Cambio de disponibilidad correctamente'))
