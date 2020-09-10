""" Products serializers """
# Django rest framework
from rest_framework import serializers
# Models
from rest_framework.validators import UniqueValidator

from scooter.apps.common.serializers import (Base64ImageField, MerchantFilteredPrimaryKeyRelatedField,
                                             StatusModelSerializer)
from scooter.apps.merchants.models import Product, CategoryProducts, ProductMenuCategory, ProductMenuOption, \
    SubcategoryProducts, SubcategorySectionProducts
# Utilities
from scooter.apps.merchants.serializers.categories import CategoryProductsModelSerializer
from scooter.utils.serializers.scooter import ScooterModelSerializer


# Serializers


class ProductMenuOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMenuOption
        fields = ('id', 'name', 'price', 'is_available')
        read_only_fields = ('id',)


class ProductMenuCategorySerializer(serializers.ModelSerializer):
    options = ProductMenuOptionSerializer(many=True)

    class Meta:
        model = ProductMenuCategory
        fields = ('id', 'name', 'is_range', 'is_obligatory', 'have_quantity', 'min_quantity', 'max_quantity',
                  'limit_options_choose', 'min_options_choose', 'max_options_choose', 'options')
        read_only_fields = ('id',)


class ProductsModelSerializer(ScooterModelSerializer):
    name = serializers.CharField(max_length=70,
                                 validators=
                                 [UniqueValidator(
                                     queryset=None,
                                     message='Ya existe un producto con ese nombre, verifique que no este desactivada')])
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    picture = Base64ImageField(required=False, allow_null=True, allow_empty_file=True)
    category_id = MerchantFilteredPrimaryKeyRelatedField(queryset=CategoryProducts.objects,
                                                         source="category")
    subcategory_id = MerchantFilteredPrimaryKeyRelatedField(queryset=SubcategoryProducts.objects,
                                                            source="subcategory", required=False, allow_null=True,
                                                            allow_empty=True)
    section_id = MerchantFilteredPrimaryKeyRelatedField(queryset=SubcategorySectionProducts.objects,
                                                        source="section", required=False, allow_null=True,
                                                        allow_empty=True)
    category = CategoryProductsModelSerializer(read_only=True)
    status = StatusModelSerializer(read_only=True)
    menu_categories = ProductMenuCategorySerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'description_long', 'stock', 'category',
                  'price', 'category_id', 'subcategory_id', 'picture', 'merchant', 'total_sales', 'status',
                  'have_menu', 'menu_categories', 'is_available', 'user', 'section_id')
        read_only_fields = ("id", "merchant", "total_sales", 'status')

    def __init__(self, *args, **kwargs):
        super(ProductsModelSerializer, self).__init__(*args, **kwargs)
        user = self.context.get('request', None)
        if user:
            self.fields['name'].validators[0].queryset = Product.objects.filter(user=user.user)

    def validate(self, data):
        merchant = self.context['merchant']
        # Send instance of product for validate of name not exist
        # product_instance = self.context.get('product_instance', None)
        # exist_product = Product.objects.filter(merchant=merchant, name=data['name']).exists()
        # if exist_product and not product_instance:
        #     raise serializers.ValidationError(
        #         {'detail': 'Ya se encuentra registrado un producto con ese nombre, verifique que no este desactivado'},
        #         code='product_exist')
        # # When is update
        # elif exist_product and product_instance and product_instance.name != data['name']:
        #     raise serializers.ValidationError(
        #         {'detail': 'Ya se encuentra registrado un producto con ese nombre, verifique que no este desactivado'},
        #         code='product_exist')

        data['merchant'] = merchant
        return data

    def create(self, data):
        try:
            menu_categories = data.pop('menu_categories', None)
            if menu_categories:
                data['have_menu'] = True
            product = super(ProductsModelSerializer, self).create(data)
            menu_option_to_save = []
            if menu_categories:
                for menu in menu_categories:
                    options = menu.pop('options', [])
                    menu_category = ProductMenuCategory.objects.create(**menu, product_id=product.id)
                    for option in options:
                        menu_option_to_save.append(ProductMenuOption(**option, menu_id=menu_category.id))

                ProductMenuOption.objects.bulk_create(menu_option_to_save)
            return product
        except Exception as ex:
            print("Exception save product, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al guardar la información'})

    def update(self, instance, data):
        picture = data.get('picture', None)
        # Delete previous image
        if picture:
            instance.picture.delete()

        return super().update(instance, data)
