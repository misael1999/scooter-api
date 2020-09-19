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
    subcategory = SubcategoryProductsModelSerializer(read_only=True)
    section = SubcategorySectionProductsSerializer(read_only=True)
    status = StatusModelSerializer(read_only=True)
    menu_categories = ProductMenuCategorySerializer(many=True, required=False)
    menu_categories_add = ProductMenuCategorySerializer(many=True, required=False)
    menu_categories_update = ProductMenuCategorySerializer(many=True, required=False)
    menu_categories_delete = ProductMenuCategorySerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'description_long', 'stock', 'category', 'subcategory',
                  'section',
                  'price', 'category_id', 'subcategory_id', 'picture', 'merchant', 'total_sales', 'status',
                  'have_menu', 'menu_categories', 'is_available', 'user', 'section_id', 'menu_add',
                  'menu_update', 'menu_delete')
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
                    menu_category = ProductMenuCategory.objects.create(**menu, product_id=product.id)
                    for option in options:
                        menu_option_to_save.append(ProductMenuOption(**option, menu_id=menu_category.id))

                ProductMenuOption.objects.bulk_create(menu_option_to_save)
            return product
        except Exception as ex:
            print("Exception save product, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al guardar la información'})

    def update(self, product, data):
        picture = data.get('picture', None)
        data.pop('menu_categories', None)
        menu_add = data.pop('menu_categories_add', [])
        menu_update = data.pop('menu_categories_update', [])
        menu_delete = data.pop('menu_categories_delete', [])
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
            menu_category_temp = ProductMenuCategory.objects.filter(pk=menu['id']).update(**menu)
            menu_category = menu_category_temp[0]
            # Actualizar el menú de la categoria
            # for field, value in menu.items():
            #     setattr(menu_category, field, value)
            # menu_category.save()
            for option in options:
                ProductMenuOption.objects.filter(pk=option['id']).update(**option)

        # Desactivar menús
        for menu in menu_delete:
            menu = ProductMenuCategory.objects.get(pk=menu['id'])
            menu.status_id = 2
            menu_option_to_delete.append(menu)
        ProductMenuCategory.objects.bulk_update(menu_delete, ['status'])
        # Delete previous image
        if picture:
            product.picture.delete()

        return super().update(product, data)
