# Django rest
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
# Permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Mixins
from scooter.apps.common.mixins import AddMerchantMixin
# Models
from scooter.apps.common.models.status import Status
# Viewset
from scooter.apps.merchants.models import Product
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant
# Serializers
from scooter.apps.promotions.serializers import MerchantPromotionSimpleSerializer, CreateMerchantPromotion
from scooter.utils.viewsets.scooter import ScooterViewSet


class MerchantPromotionViewSet(ScooterViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                               mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin, AddMerchantMixin):

    serializer_class = MerchantPromotionSimpleSerializer
    queryset = Product.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerMerchant)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name', 'description')
    ordering_fields = ('created', 'name', 'description')
    # Affect the default order
    ordering = ('-created', '-name')
    filter_fields = ('status', 'promotion_type')
    """ Method dispatch in AddMerchantMixin """
    merchant = None

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active categories """
        if self.action == 'list':
            return self.merchant.merchantpromotion_set.all()
        return self.queryset

    def create(self, request, *args, **kwargs):
        """ To return a custom response """
        serializer = CreateMerchantPromotion(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(data=MerchantPromotionSimpleSerializer(obj).data, status=status.HTTP_201_CREATED)
    #
    # def update(self, request, *args, **kwargs):
    #     product = self.get_object()
    #     # Send instance of product for validate of name not exist
    #     self.product_instance = product
    #     serializer = self.get_serializer(product, data=request.data, partial=True,
    #                                      context=self.get_serializer_context())
    #     serializer.is_valid(raise_exception=True)
    #     product = serializer.save()
    #     product_created = ProductsModelSerializer(product).data
    #     data = self.set_response(status=True, data=product_created, message="Producto actualizado correctamente")
    #     return Response(data=data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        try:
            sts = Status.objects.get(slug_name='inactive')
            instance.status = sts
            instance.save()
        except Status.DoesNotExist:
            error = self.set_error_response(status=False, field='status',
                                            message='Ha ocurrido un error al borrar el producto')
            return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['PATCH'])
    def unlock(self, request, *args, **kwargs):
        product = self.get_object()
        sts = Status.objects.get(slug_name='active')
        # Send instance of product for validate of name not exist
        product.status = sts
        product.save()
        data = self.set_response(status=True, data={}, message="Producto activado correctamente")
        return Response(data=data, status=status.HTTP_200_OK)
