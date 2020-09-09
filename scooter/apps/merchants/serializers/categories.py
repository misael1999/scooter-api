""" Categories serializers """
# Django rest framework
from rest_framework import serializers
# Models
from rest_framework.validators import UniqueValidator

from scooter.apps.common.serializers import Base64ImageField, StatusModelSerializer
from scooter.apps.merchants.models import CategoryProducts, Product, ProductMenuOption, ProductMenuCategory, \
    SubcategoryProducts
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


class SubcategoryProductsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubcategoryProducts
        fields = ('id', 'name', 'user', 'picture', 'merchant', 'category', 'status')
        read_only_fields = ('id', 'status', 'merchant', 'category')


class CategoryProductsModelSerializer(ScooterModelSerializer):
    name = serializers.CharField(max_length=70,
                                 validators=
                                 [UniqueValidator(
                                     queryset=None,
                                     message='Ya existe una categoria con ese nombre, verifique que no este desactivada')])
    picture = Base64ImageField(required=False, allow_null=True, allow_empty_file=True)
    status = StatusModelSerializer(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    subcategories = SubcategoryProductsModelSerializer(serializers.ModelSerializer,
                                                       many=True, required=False,
                                                       allow_null=True)

    class Meta:
        model = CategoryProducts
        fields = ("id", 'name', 'picture', 'status', 'user', 'subcategories')
        read_only_fields = ("id", "status")

    def __init__(self, *args, **kwargs):
        super(CategoryProductsModelSerializer, self).__init__(*args, **kwargs)
        user = self.context.get('request', None)
        if user:
            self.fields['name'].validators[0].queryset = CategoryProducts.objects.filter(user=user.user)

    def create(self, data):
        try:
            merchant = self.context['merchant']
            data['merchant'] = merchant
            subcategories = data.pop('subcategories', [])
            category = CategoryProducts.objects.create(**data)
            subcategories_to_save = []
            for subcategory in subcategories:
                subcategories_to_save.append(SubcategoryProducts(**subcategory,
                                                                 user=data['user'],
                                                                 merchant=merchant,
                                                                 category=category))
            SubcategoryProducts.objects.bulk_create(subcategories_to_save)
            data['subcategories'] = subcategories
            return data
        except Exception as ex:
            serializers.ValidationError({'detail': 'Ha ocurrido un error al registrar la categoría'})

    def update(self, instance, data):
        picture = data.get('picture', None)
        # Delete previous image
        if picture:
            instance.picture.delete()

        return super().update(instance, data)


class CategoryWithProductsSerializer(serializers.ModelSerializer):
    # products = ProductSimpleModelSerializer(many=True, read_only=True)

    class Meta:
        model = CategoryProducts
        fields = ('id', 'name', 'picture')
        read_only_fields = fields
