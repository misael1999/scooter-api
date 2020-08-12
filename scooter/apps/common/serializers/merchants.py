from rest_framework import serializers
# Models
from scooter.apps.common.models import TypeAddress, CategoryMerchant, SubcategoryMerchant


class CategoryMerchantModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryMerchant
        fields = ('id', 'name', 'slug_name')
        read_only_fields = ('id', 'name', 'slug_name')


class SubcategoryMerchantModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubcategoryMerchant
        fields = ('id', 'name', 'slug_name')
        read_only_fields = ('id', 'name', 'slug_name')
