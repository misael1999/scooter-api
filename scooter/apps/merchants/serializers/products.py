""" Products serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.serializers import Base64ImageField
from scooter.apps.merchants.models import Product, CategoryProducts
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer
# Serializers


class ProductsModelSerializer(ScooterModelSerializer):
    picture = Base64ImageField(required=False, allow_null=True, allow_empty_file=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=CategoryProducts.objects.all(), source="category")
    status = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'description_long', 'stock',
                  'price', 'category_id', 'picture', 'merchant', 'total_sales', 'status')
        read_only_fields = ("id", "merchant", "total_sales", 'status')

    def validate(self, data):
        merchant = self.context['merchant']
        # Send instance of product for validate of name not exist
        product_instance = self.context.get('product_instance', None)
        exist_product = Product.objects.filter(merchant=merchant, name=data['name']).exists()
        if exist_product and not product_instance:
            raise serializers.ValidationError(
                {'detail': 'Ya se encuentra registrado un producto con ese nombre, verifique que no este desactivado'},
                code='product_exist')
        # When is update
        elif exist_product and product_instance and product_instance.name != data['name']:
            raise serializers.ValidationError(
                {'detail': 'Ya se encuentra registrado un producto con ese nombre, verifique que no este desactivado'},
                code='product_exist')

        data['merchant'] = merchant
        return data

    def update(self, instance, data):
        picture = data.get('picture', None)
        # Delete previous image
        if picture:
            instance.picture.delete()

        return super().update(instance, data)
