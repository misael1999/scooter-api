# Django rest
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

from scooter.apps.merchants.models import Merchant
# Permissions
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Models
from scooter.apps.stations.models.stations import Station
# Serializers
from scooter.apps.merchants.serializers import (MerchantSignUpSerializer,
                                                MerchantWithAllInfoSerializer)

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
    pagination_class = None
    lookup_field = 'id'
    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('merchant_name', 'category__name', 'subcategory__name')
    ordering_fields = ('-reputation',)
    ordering = ('-reputation', 'created')
    filter_fields = ('reputation', 'category', 'subcategory')

    def get_queryset(self):
        if self.action == 'list':
            return Merchant.objects.filter(status__slug_name='active', information_is_complete=True)
        return self.queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        data = self.set_response(status='ok',
                                 data=response.data,
                                 message='Listado de comercios')

        return Response(data, status=status.HTTP_200_OK)

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
            permission_classes = [IsAuthenticated, IsAccountOwnerMerchant]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """ Station sign up """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = self.set_response(status='ok',
                                 data={},
                                 message='Se ha registrado un nuevo comercio')
        return Response(data, status=status.HTTP_201_CREATED)

    #
    # @action(detail=True, methods=('PATCH', 'PUT'))
    # def update_info(self, request, *args, **kwargs):
    #     try:
    #         station = self.get_object()
    #         partial = request.method == 'PATCH'
    #         serializer = StationUpdateInfoSerializer(station, data=request.data, partial=partial)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         data = StationUserModelSerializer(station).data
    #     except Station.DoesNotExist:
    #         return Response(
    #             self.set_error_response(status=False, field='Detail', message='No existe la central'))
    #     return Response(self.set_response(status='ok', data=data, message='Información actualizada correctamente'))
