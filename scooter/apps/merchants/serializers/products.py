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
from scooter.apps.merchants.serializers.subcategories import SubcategoryProductsModelSerializer, \
    SubcategorySectionProductsSerializer
from scooter.utils.serializers.scooter import ScooterModelSerializer


# Serializers
class ProductMenuOptionSerializer(serializers.ModelSerializer):
    option_id = serializers.IntegerField(required=False, allow_null=True, source="id")
    status = StatusModelSerializer(read_only=True)

    class Meta:
        model = ProductMenuOption
        fields = ('option_id', 'id', 'name', 'price', 'is_available', 'status')
        read_only_fields = ('id', 'status')


class ProductMenuCategorySerializer(serializers.ModelSerializer):
    options = ProductMenuOptionSerializer(many=True)
    menu_id = serializers.IntegerField(required=False, allow_null=True, source="id")
    status = StatusModelSerializer(read_only=True)

    class Meta:
        model = ProductMenuCategory
        fields = ('id', 'menu_id', 'name', 'is_range', 'is_obligatory', 'have_quantity', 'min_quantity', 'max_quantity',
                  'limit_options_choose', 'min_options_choose',
                  'max_options_choose', 'options', 'is_option_repeatable', 'status')
        read_only_fields = ('status', 'id')


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
    subcategory = SubcategoryProductsModelSerializer(read_only=True)
    section = SubcategorySectionProductsSerializer(read_only=True)
    status = StatusModelSerializer(read_only=True)
    menu_categories = ProductMenuCategorySerializer(many=True, required=False)
    menu_categories_add = ProductMenuCategorySerializer(many=True, required=False)
    menu_categories_update = ProductMenuCategorySerializer(many=True, required=False)
    menu_categories_delete = ProductMenuCategorySerializer(many=True, required=False)
    menu_categories_active = ProductMenuCategorySerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'description_long', 'stock', 'category', 'subcategory',
                  'section',
                  'price', 'category_id', 'subcategory_id', 'picture', 'merchant', 'total_sales', 'status',
                  'have_menu', 'menu_categories', 'is_available', 'user', 'section_id', 'menu_categories_add',
                  'menu_categories_update', 'menu_categories_delete', 'menu_categories_active')
        read_only_fields = ("id", "merchant", "total_sales", 'status')

    def __init__(self, *args, **kwargs):
        super(ProductsModelSerializer, self).__init__(*args, **kwargs)
        user = self.context.get('request', None)
        if user:
            self.fields['name'].validators[0].queryset = Product.objects.filter(user=user.user)

    def validate(self, data):
        merchant = self.context['merchant']
        data['merchant'] = merchant
        return data

    def create(self, data):
        try:
            menu_categories = data.pop('menu_categories', None)
            menu_add = data.pop('menu_categories_add', [])
            menu_update = data.pop('menu_categories_update', [])
            menu_delete = data.pop('menu_categories_delete', [])
            if menu_categories:
                data['have_menu'] = True
            product = super(ProductsModelSerializer, self).create(data)
            menu_option_to_save = []
            if menu_categories:
                for menu in menu_categories:
                    options = menu.pop('options', [])
                    menu_id = menu.pop('menu_id', None)
                    menu_category = ProductMenuCategory.objects.create(**menu, product_id=product.id)
                    for option in options:
                        option_id = option.pop('option_id', None)
                        menu_option_to_save.append(ProductMenuOption(**option, menu_id=menu_category.id))

                ProductMenuOption.objects.bulk_create(menu_option_to_save)
            return product
        except Exception as ex:
            print("Exception save product, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al guardar la información'})

    def update(self, product, data):
        data.pop('menu_categories', None)
        menu_add = data.pop('menu_categories_add', [])
        menu_update = data.pop('menu_categories_update', [])
        menu_delete = data.pop('menu_categories_delete', [])
        menu_active = data.pop('menu_categories_active', [])
        menu_option_to_save = []
        menu_option_to_update = []
        menu_option_to_delete = []

        # Agregar nuevos menus
        for menu in menu_add:
            options = menu.pop('options', [])
            menu_category = ProductMenuCategory.objects.create(**menu, product_id=product.id)
            for option in options:
                menu_option_to_save.append(ProductMenuOption(**option, menu_id=menu_category.id))
        ProductMenuOption.objects.bulk_create(menu_option_to_save)

        # Actualizar menús
        for menu in menu_update:
            options = menu.pop('options', [])
            menu_id = menu.pop('id', None)
            menu_category = ProductMenuCategory.objects.get(pk=menu_id)
            # menu_category = menu_category_temp[0]
            # Actualizar el menú de la categoria
            for field, value in menu.items():
                setattr(menu_category, field, value)
            menu_category.save()
            for option in options:
                option_id = option.pop('id', None)
                if option_id:
                    ProductMenuOption.objects.filter(pk=option_id).update(**option)
                else:
                    ProductMenuOption.objects.create(**option, menu=menu_category)

        # Desactivar menús
        for menu in menu_delete:
            menu = ProductMenuCategory.objects.get(pk=menu['id'])
            menu.status_id = 2
            menu_option_to_delete.append(menu)
        ProductMenuCategory.objects.bulk_update(menu_option_to_delete, ['status'])
        # Activar menús
        for menu in menu_active:
            menu = ProductMenuCategory.objects.get(pk=menu['id'])
            menu.status_id = 1
            menu_option_to_delete.append(menu)
        ProductMenuCategory.objects.bulk_update(menu_option_to_delete, ['status'])

        picture = data.get('picture', None)
        # Delete previous image
        if picture:
            product.picture.delete()

        return super().update(product, data)
