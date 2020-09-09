""" Categories serializers """
# Django rest framework
from rest_framework import serializers
# Models
from rest_framework.validators import UniqueValidator

from scooter.apps.common.serializers import Base64ImageField, StatusModelSerializer
from scooter.apps.merchants.models import CategoryProducts, Product, ProductMenuOption, ProductMenuCategory
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


class CategoryProductsModelSerializer(ScooterModelSerializer):
    name = serializers.CharField(max_length=70,
                                 validators=
                                 [UniqueValidator(
                                     queryset=None,
                                     message='Ya existe una categoria con ese nombre, verifique que no este desactivada')])
    picture = Base64ImageField(required=False, allow_null=True, allow_empty_file=True)
    status = StatusModelSerializer(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CategoryProducts
        fields = ("id", 'name', 'picture', 'status', 'user')
        read_only_fields = ("id", "status")

    def __init__(self, *args, **kwargs):
        super(CategoryProductsModelSerializer, self).__init__(*args, **kwargs)
        user = self.context.get('request', None)
        if user:
            self.fields['name'].validators[0].queryset = CategoryProducts.objects.filter(user=user.user)

    def validate(self, data):
        merchant = self.context['merchant']
        # Send instance of category for validate of name not exist
        # category_instance = self.context.get('category_instance', None)
        # exist_category = CategoryProducts.objects.filter(merchant=merchant, name=data['name']).exists()
        # if exist_category and not category_instance:
        #     raise serializers.ValidationError(
        #         {'detail': 'Ya se encuentra registrado una categoría con ese nombre, verifique que no este desactivada'},
        #         code='category_exist')
        # # When is update
        # elif exist_category and category_instance and category_instance.name != data['name']:
        #     raise serializers.ValidationError(
        #         {'detail': 'Ya se encuentra registrado un categoría con ese nombre, verifique que no este desactivada'},
        #         code='category_exist')

        data['merchant'] = merchant
        return data

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
