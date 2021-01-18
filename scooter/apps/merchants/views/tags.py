# Django rest
# Mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
# Permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from scooter.apps.common.mixins import AddMerchantMixin
from scooter.apps.common.models import Status
from scooter.apps.customers.permissions import IsStation
from scooter.apps.merchants.models import MerchantTag, Tag
# Serializers
from scooter.apps.merchants.serializers import MerchantTagModelSerializer, TagModelSerializer, TagModelSimpleSerializer, \
    CreateMerchantTagSerializer, MerchantTagSimpleSerializer

# Utilities
from scooter.utils.viewsets import ScooterViewSet


class MerchantTagViewSet(ScooterViewSet, mixins.ListModelMixin,
                         mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                         mixins.UpdateModelMixin, mixins.DestroyModelMixin, AddMerchantMixin):
    """ Handle add payment methods """
    queryset = MerchantTag.objects.all()
    permission_classes = (IsAuthenticated, IsStation)
    serializer_class = MerchantTagModelSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('tag_name',)
    # ordering_fields = ('name',)
    # filter_fields = ('status',)
    lookup_field = 'id'
    merchant = None

    # def get_permissions(self):
    #     permission_classes = []
    #     if self.action in ['create', 'update', 'destroy', 'perform_destroy']:
    #         permission_classes = [IsAuthenticated, IsStation]
    #     if self.action in ['list']:
    #         permission_classes = [AllowAny]
    #
    #     return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return MerchantTagSimpleSerializer
        if self.action == 'create':
            return CreateMerchantTagSerializer
        return self.serializer_class

    # def perform_destroy(self, instance):
    #     try:
    #         sts = Status.objects.get(slug_name='inactive')
    #         instance.status = sts
    #         instance.save()
    #     except Status.DoesNotExist:
    #         error = self.set_error_response(status=False, field='status',
    #                                         message='Ha ocurrido un error al borrar la etiqueta')
    #         return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TagViewSet(ScooterViewSet, mixins.ListModelMixin,
                 mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                 mixins.DestroyModelMixin):

    queryset = Tag.objects.all()
    serializer_class = TagModelSerializer
    permission_classes = (IsAuthenticated, IsStation)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('name',)
    ordering_fields = ('name',)
    filter_fields = ('status',)
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'list':
            return TagModelSimpleSerializer
        return self.serializer_class
