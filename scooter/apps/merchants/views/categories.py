# Django rest
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Models
from scooter.apps.common.models.status import Status
# Serializers
from scooter.apps.merchants.serializers import SubcategoryProductsModelSerializer, \
    SubcategoryProductsModelSimpleSerializer
from scooter.apps.merchants.serializers.categories import (CategoryProductsModelSerializer,
                                                           CategoryWithProductsSerializer, ProductSimpleModelSerializer,
                                                           CategoryWithSubcategoriesSerializer, CategoryProductsSimpleModelSerializer)
# Viewset
from scooter.apps.merchants.models import CategoryProducts, Product
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins import AddMerchantMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CategoriesProductsViewSet(ScooterViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                                mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin, AddMerchantMixin):
    """ View set for the merchants can register a new category """

    serializer_class = CategoryProductsModelSerializer
    queryset = CategoryProducts.objects.all()
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name',)
    ordering_fields = ('created', 'name')
    # Affect the default order
    ordering = ('-created',)
    filter_fields = ('status',)
    """ Method dispatch in AddMerchantMixin """
    merchant = None
    category_instance = None

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active categories """
        if self.action == 'list':
            return self.merchant.categoryproducts_set.all()
        return self.queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAccountOwnerMerchant]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        """ Add instance of category to serializer context """
        context = super(CategoriesProductsViewSet, self).get_serializer_context()
        # Send instance of category for validate of name not exist
        context['category_instance'] = self.category_instance
        return context

    def create(self, request, *args, **kwargs):
        """ To return a custom response """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data=CategoryProductsModelSerializer(obj).data,
                                 message='Se ha registrado un nuevo categoría')
        return Response(data=data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        category = self.get_object()
        # Send instance of category for validate of name not exist
        self.category_instance = category
        serializer = self.get_serializer(category, data=request.data, partial=True,
                                         context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        category_created = CategoryProductsModelSerializer(category).data
        data = self.set_response(status=True, data=category_created, message="Categoría actualizada correctamente")
        return Response(data=data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        try:
            sts = Status.objects.get(slug_name='inactive')
            instance.status = sts
            instance.save()
        except Status.DoesNotExist:
            error = self.set_error_response(status=False, field='status',
                                            message='Ha ocurrido un error al borrar la categoria')
            return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['PATCH'])
    def unlock(self, request, *args, **kwargs):
        category = self.get_object()
        sts = Status.objects.get(slug_name='active')
        # Send instance of category for validate of name not exist
        category.status = sts
        category.save()
        data = self.set_response(status=True, data={}, message="Categoría activada correctamente")
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def products(self, request, *args, **kwargs):
        search = request.query_params.get('search', None)
        list_categories = []
        products_ids = []
        if search:
            products = Product.objects.filter(name__icontains=search, status__slug_name="active")
            products_ids = products.values_list('id', flat=True)
            data = {'name': 'RESULTADOS: {} ELEMENTOS'.format(products.count()),
                    'products': ProductSimpleModelSerializer(products, many=True).data}
            list_categories.append(data)

        categories = self.merchant.categoryproducts_set.filter(status__slug_name="active")
        # data = CategoryWithProductsSerializer(categories, many=True).data
        # For filter by status, get only actives
        for category in categories:
            category_temp = CategoryWithProductsSerializer(category).data
            category_temp['products'] = ProductSimpleModelSerializer(category.products.filter(
                status__slug_name="active").exclude(id__in=products_ids), many=True).data
            list_categories.append(category_temp)

        response = self.set_response(status=True, data=list_categories, message="Productos con sus categorias")
        return Response(data=response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path="products/search")
    def search(self, request, *args, **kwargs):
        search = request.query_params.get('search', None)
        list_categories = []
        if search:
            products = Product.objects.filter(name__icontains=search, status__slug_name="active")
            data = {'name': 'RESULTADOS: {} ELEMENTOS'.format(products.count()),
                    'products': ProductSimpleModelSerializer(products, many=True).data}
            list_categories.append(data)

        response = self.set_response(status=True, data=list_categories, message="Busqueda de solo los productos")
        return Response(data=response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def products_cat(self, request, *args, **kwargs):
        category = self.get_object()
        category_temp = CategoryWithProductsSerializer(category).data
        category_temp['products'] = ProductSimpleModelSerializer(category.products.filter(
            status__slug_name="active"), many=True).data
        return Response(data=category_temp, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def level_two(self, request, *args, **kwargs):
        categories = self.merchant.categoryproducts_set.filter(status__slug_name="active")
        list_categories = CategoryProductsSimpleModelSerializer(categories, many=True).data
        response = self.set_response(status=True, data=list_categories, message="Categorias sin paginación")
        return Response(data=response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def level_three(self, request, *args, **kwargs):
        categories = self.merchant.categoryproducts_set.filter(status__slug_name="active")
        list_categories = []
        for category in categories:
            category_temp = CategoryProductsSimpleModelSerializer(category).data
            queryset_ = category.subcategories.filter(status__slug_name="active")
            category_temp['subcategories'] = SubcategoryProductsModelSerializer(queryset_, many=True).data
            list_categories.append(category_temp)
        response = self.set_response(status=True, data=list_categories, message="Categorias con subcategorias")
        return Response(data=response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path="subcategories/products")
    def group_subcategories(self, request, *args, **kwargs):
        category = self.get_object()
        category_temp = CategoryProductsSimpleModelSerializer(category).data
        subcategories_set = category.subcategories.filter(status__slug_name="active")
        subcategories_temp = []
        for subcategory_s in subcategories_set:
            subcategory_temp = SubcategoryProductsModelSimpleSerializer(subcategory_s).data
            subcategory_temp['products'] = ProductSimpleModelSerializer(subcategory_s.products.filter(
                status__slug_name="active"), many=True).data
            subcategories_temp.append(subcategory_temp)
        category_temp['subcategories'] = subcategories_temp
        response = self.set_response(status=True, data=category_temp, message="Productos agrupado por subcategorias")
        return Response(data=response, status=status.HTTP_200_OK)

