# Django rest
from rest_framework import mixins, status
from rest_framework.response import Response
# Models
from scooter.apps.customers.models.customers import CustomerAddress
from scooter.apps.common.models.status import Status
# Serializers
from scooter.apps.customers.serializers.addresses import (CustomerAddressModelSerializer,
                                                          AddressRecommendationsSerializer)
# Viewset
from scooter.utils.viewsets.scooter import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class RecommendationsAddressesViewSet(ScooterViewSet, mixins.ListModelMixin,
                                      mixins.CreateModelMixin, mixins.UpdateModelMixin,
                                      mixins.DestroyModelMixin):
    """ View set for the general can register a new address for recommendations """

    serializer_class = CustomerAddressModelSerializer
    queryset = CustomerAddress.objects.filter(type_address_id=3, status__slug_name="active")
    permission_classes = (IsAuthenticated, )
    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('alias', 'full_address', 'category')
    # ordering_fields = ('created',)
    # Affect the default order
    ordering = ('-created', '-alias', '-category')
    filter_fields = ('category',)

    def create(self, request, *args, **kwargs):
        """ Create address recommendations """
        serializer = AddressRecommendationsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data={},
                                 message='Se ha registrado una nueva dirección de recomendaciones')
        return Response(data=data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        address = self.get_object()

        serializer = AddressRecommendationsSerializer(address, data=request.data, partial=True,
                                                      context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        address = serializer.save()
        # address_created = CustomerAddressModelSerializer(address).data
        data = self.set_response(status=True, data={}, message="Dirección actualizada correctamente")
        return Response(data=data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        try:
            sts = Status.objects.get(slug_name='deleted')
            instance.status_id = sts
            instance.save()
        except Status.DoesNotExist:
            error = self.set_error_response(status=False, field='status',
                                            message='Ha ocurrido un error al borrar la dirección')
            return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

