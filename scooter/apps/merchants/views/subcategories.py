# Django rest
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Models
from scooter.apps.common.models.status import Status
# Serializers
from scooter.apps.merchants.models import SubcategoryProducts
from scooter.apps.merchants.serializers.categories import (ProductSimpleModelSerializer, )
# Viewset
from scooter.apps.merchants.serializers.subcategories import SubcategoryWithProductsSerializer, \
    SubcategorySectionProductsSerializer
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins import AddMerchantMixin
# Permissions
from rest_framework.permissions import IsAuthenticated


class SubcategoriesProductsViewSet(ScooterViewSet, AddMerchantMixin, mixins.DestroyModelMixin):
    """ View set for the merchants can register a new category """
    """ Method dispatch in AddMerchantMixin """
    merchant = None
    queryset = SubcategoryProducts.objects.all()
    permission_classes = (IsAuthenticated,)

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

    @action(detail=True, methods=['GET'])
    def products(self, request, *args, **kwargs):
        subcategory = self.get_object()
        subcategory_temp = SubcategoryWithProductsSerializer(subcategory).data
        subcategory_temp['products'] = ProductSimpleModelSerializer(subcategory.products.filter(
            status__slug_name="active"), many=True).data
        return Response(data=subcategory_temp, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path="products/sections")
    def products_sections(self, request, *args, **kwargs):
        subcategory = self.get_object()

        subcategory_temp = SubcategoryWithProductsSerializer(subcategory).data
        list_sections = []
        for section in subcategory.sections.filter(status__slug_name="active"):
            section_temp = SubcategorySectionProductsSerializer(section).data
            section_temp['products'] = ProductSimpleModelSerializer(section.products.filter(
                status__slug_name="active"), many=True).data
            list_sections.append(section_temp)
        subcategory_temp['sections'] = list_sections
        return Response(data=subcategory_temp, status=status.HTTP_200_OK)
