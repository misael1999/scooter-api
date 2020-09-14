""" Categories serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.serializers import Base64ImageField, StatusModelSerializer
from scooter.apps.merchants.models import CategoryProducts, Product, ProductMenuOption, ProductMenuCategory, \
    SubcategoryProducts, SubcategorySectionProducts
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer


class ProductMenuOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMenuOption
        fields = ('id', 'name', 'price')
        read_only_fields = ('id',)


class ProductMenuCategorySerializer(serializers.ModelSerializer):
    options = ProductMenuOptionSerializer(many=True)

    class Meta:
        model = ProductMenuCategory
        fields = ('id', 'name', 'is_range', 'is_obligatory', 'have_quantity', 'min_quantity', 'max_quantity',
                  'limit_options_choose', 'min_options_choose', 'max_options_choose', 'options')
        read_only_fields = ('id',)


# Serializers
class ProductSimpleModelSerializer(ScooterModelSerializer):
    menu_categories = ProductMenuCategorySerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'description_long', 'stock', 'category',
                  'price', 'category_id', 'picture', 'merchant', 'status',  'menu_categories', 'is_available')
        read_only_fields = fields


class SubcategorySectionProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubcategorySectionProducts
        fields = ('id', 'name')
        read_only_fields = ('id',)


class SubcategoryProductsModelSerializer(serializers.ModelSerializer):
    sections = SubcategorySectionProductsSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = SubcategoryProducts
        fields = ('id', 'name', 'user', 'picture', 'merchant', 'category', 'status', 'sections')
        read_only_fields = ('id', 'status', 'merchant', 'category')


class SubcategoryProductsModelSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubcategoryProducts
        fields = ('id', 'name', 'user', 'picture', 'merchant', 'category', 'status')
        read_only_fields = ('id', 'status', 'merchant', 'category')


class SubcategoryWithProductsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubcategoryProducts
        fields = ('id', 'name', 'picture')
        read_only_fields = fields
