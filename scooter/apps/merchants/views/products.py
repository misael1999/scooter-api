# Django rest
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Models
from scooter.apps.common.models.status import Status
# Serializers
from scooter.apps.merchants.serializers import ProductsModelSerializer
# Viewset
from scooter.apps.merchants.models import Product
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins import AddMerchantMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class ProductsViewSet(ScooterViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin, AddMerchantMixin):
    """ View set for the merchants can register a new product """

    serializer_class = ProductsModelSerializer
    queryset = Product.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerMerchant)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name', 'category__name', 'description')
    ordering_fields = ('created', 'name', 'description')
    # Affect the default order
    ordering = ('-created', '-name')
    filter_fields = ('status', 'category')
    """ Method dispatch in AddMerchantMixin """
    merchant = None
    product_instance = None

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active categories """
        if self.action == 'list':
            return self.merchant.product_set.all()
        return self.queryset

    def get_serializer_context(self):
        """ Add instance of product to serializer context """
        context = super(ProductsViewSet, self).get_serializer_context()
        # Send instance of product for validate of name not exist
        context['product_instance'] = self.product_instance
        return context

    def create(self, request, *args, **kwargs):
        """ To return a custom response """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data=ProductsModelSerializer(obj).data,
                                 message='Se ha registrado un nuevo producto')
        return Response(data=data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        # Send instance of product for validate of name not exist
        self.product_instance = product
        serializer = self.get_serializer(product, data=request.data, partial=True,
                                         context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        product_created = ProductsModelSerializer(product).data
        data = self.set_response(status=True, data=product_created, message="Producto actualizado correctamente")
        return Response(data=data, status=status.HTTP_201_CREATED)

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
