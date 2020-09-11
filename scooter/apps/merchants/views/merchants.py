# Django rest
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

from scooter.apps.merchants.models import Merchant
# Permissions
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant, IsSameMerchant
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Models
# Serializers
from scooter.apps.merchants.serializers import (MerchantSignUpSerializer,
                                                MerchantWithAllInfoSerializer, UpdateInfoMerchantSerializer,
                                                AvailabilityMerchantSerializer, ChangePasswordMerchantSerializer)

from scooter.apps.users.serializers.users import UserModelSimpleSerializer
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class MerchantViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.UpdateModelMixin):
    """ Handle signup and update of merchant """
    queryset = Merchant.objects.all()
    serializer_class = MerchantWithAllInfoSerializer
    lookup_field = 'id'
    # Filters
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('merchant_name',)
    ordering_fields = ('is_open', 'reputation', 'created')
    ordering = ('-is_open', '-reputation', 'created')
    filter_fields = ('category', 'subcategory')

    def get_queryset(self):
        if self.action == 'list':
            return Merchant.objects.filter(status__slug_name='active', information_is_complete=True)
        return self.queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create':
            serializer_class = MerchantSignUpSerializer
        if self.action in ['list', 'retrieve']:
            serializer_class = MerchantWithAllInfoSerializer
        return serializer_class

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['partial_update', 'update', 'update_info']:
            permission_classes = [IsAuthenticated, IsSameMerchant]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

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

    @action(detail=True, methods=('PATCH', 'PUT'))
    def update_info(self, request, *args, **kwargs):
        try:
            merchant = self.get_object()
            partial = request.method == 'PATCH'
            serializer = UpdateInfoMerchantSerializer(merchant, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = {}
        except Merchant.DoesNotExist:
            return Response(
                self.set_error_response(status=False, field='Detail', message='No existe el comercio'))
        return Response(self.set_response(status='ok', data=data, message='Información actualizada correctamente')) \


    @action(detail=True, methods=('PUT',))
    def update_availability(self, request, *args, **kwargs):
        merchant = self.get_object()
        serializer = AvailabilityMerchantSerializer(merchant, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        status_availability = serializer.save()
        return Response(self.set_response(status='ok', data={'status': status_availability},
                                          message='Cambio de disponibilidad correctamente'))

    @action(detail=True, methods=('PATCH', ))
    def change_password(self, request, *args, **kwargs):
        customer = self.get_object()
        partial = request.method == 'PATCH'
        serializer = ChangePasswordMerchantSerializer(customer, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.set_response(status='ok', data={},
                                          message='Contraseña actualizada correctamente'))
