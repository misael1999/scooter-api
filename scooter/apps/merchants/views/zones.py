# Django rest
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
# Mixins
from rest_framework import mixins
from scooter.apps.common.mixins import AddMerchantMixin
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

# Models
from scooter.apps.common.models import Status
from scooter.apps.merchants.models import MerchantZone
# Serializers
from scooter.apps.merchants.serializers import MerchantZoneSerializer
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Permissions
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant


class MerchantZoneViewSet(ScooterViewSet, mixins.ListModelMixin,
                          mixins.CreateModelMixin, mixins.UpdateModelMixin,
                          mixins.RetrieveModelMixin, AddMerchantMixin, mixins.DestroyModelMixin):
    """ Handle add zones """
    queryset = MerchantZone.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerMerchant)
    serializer_class = MerchantZoneSerializer
    lookup_field = 'id'
    merchant = None

    def perform_destroy(self, instance):
        try:
            sts = Status.objects.get(slug_name='inactive')
            instance.status = sts
            instance.save()
        except Status.DoesNotExist:
            error = self.set_error_response(status=False, field='status',
                                            message='Ha ocurrido un error al desactivar la zona')
            return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['PATCH'])
    def unlock(self, request, *args, **kwargs):
        zone = self.get_object()
        sts = Status.objects.get(slug_name='active')
        # Send instance of zone for validate of name not exist
        zone.status = sts
        zone.save()
        data = self.set_response(status=True, data={}, message="Zona activada correctamente")
        return Response(data=data, status=status.HTTP_200_OK)
    # def get_permissions(self):
    #     permission_classes = []
    #     if self.action in ['create', 'update', 'destroy', 'perform_destroy']:
    #         permission_classes = [IsAuthenticated, IsAccountOwnerMerchant]
    #     if self.action in ['list']:
    #         permission_classes = [IsAuthenticated]
    #
    #     return [permission() for permission in permission_classes]
