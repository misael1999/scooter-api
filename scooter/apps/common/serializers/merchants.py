from rest_framework import serializers
# Models
from scooter.apps.common.models import TypeAddress, CategoryMerchant, SubcategoryMerchant
from scooter.apps.common.serializers import StatusModelSerializer


class SubcategoryMerchantModelSerializer(serializers.ModelSerializer):

    status = StatusModelSerializer(read_only=True)

    class Meta:
        model = SubcategoryMerchant
        fields = ('id', 'name', 'image', 'slug_name', 'status')
        read_only_fields = ('id', 'name', 'image', 'slug_name')


class CategoryMerchantModelSerializer(serializers.ModelSerializer):
    subcategories = SubcategoryMerchantModelSerializer(many=True)
    status = StatusModelSerializer(read_only=True)

    class Meta:
        model = CategoryMerchant
        fields = ('id', 'name', 'image', 'slug_name', 'subcategories', 'status')
        read_only_fields = ('id', 'name', 'image', 'slug_name', 'subcategories', 'status')

