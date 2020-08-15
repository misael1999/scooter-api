from rest_framework import serializers
# Models
from scooter.apps.common.models import TypeAddress, CategoryMerchant, SubcategoryMerchant


class SubcategoryMerchantModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubcategoryMerchant
        fields = ('id', 'name', 'image', 'slug_name')
        read_only_fields = ('id', 'name', 'image', 'slug_name')


class CategoryMerchantModelSerializer(serializers.ModelSerializer):

    subcategories = SubcategoryMerchantModelSerializer(many=True)

    class Meta:
        model = CategoryMerchant
        fields = ('id', 'name', 'image' 'slug_name', 'subcategories')
        read_only_fields = ('id', 'name', 'image', 'slug_name', 'subcategories')



