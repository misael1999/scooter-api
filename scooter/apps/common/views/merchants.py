# Django rest
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
# Models
from scooter.apps.common.models import CategoryMerchant
from scooter.utils.viewsets import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated
# Models

# Serializers
from scooter.apps.common.serializers import (CategoryMerchantModelSerializer, SubcategoryMerchantModelSerializer)


class CategoryMerchantViewSet(ScooterViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    """ Return merchant categories"""
    serializer_class = CategoryMerchantModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.action == 'list':
            return CategoryMerchant.objects.filter(status__slug_name="active")

        return CategoryMerchant.objects.all()

    @action(detail=True, methods=['GET'])
    def subcategories(self, request, *args, **kwargs):
        category_merchant = self.get_object()
        queryset = category_merchant.subcategorymerchant_set.all()
        serializer = SubcategoryMerchantModelSerializer(queryset, many=True).data
        data = self.set_response(status=True, data=serializer, message="Listado de subcategorias")
        return Response(data=data, status=status.HTTP_200_OK)
