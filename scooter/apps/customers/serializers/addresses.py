""" Customers serializers """
# Django
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.customers.models import CustomerAddress
# Serializers
from scooter.utils.serializers.scooter import ScooterModelSerializer
from django.contrib.gis.geos import Point


class CustomerAddressModelSerializer(serializers.ModelSerializer):
    type_address = serializers.StringRelatedField(read_only=True)
    status = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CustomerAddress
        geo_field = 'point'
        fields = ("id", "alias", "full_address", "street", "suburb",
                  "postal_code", "exterior_number", 'type_address',
                  "inside_number", "references", "status", "point",)
        read_only_fields = fields


# Help serializer
class PointSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class CreateCustomerAddressSerializer(serializers.ModelSerializer):
    point = PointSerializer()
    type_address_id = serializers.IntegerField(default=1)

    class Meta:
        model = CustomerAddress
        fields = ("alias", "full_address", "type_address_id", "exterior_number",
                  "inside_number", "references", "point")

    def validate(self, data):

        customer = self.context['customer']
        # Send instance of vehicle for validate of name not exist
        address_instance = self.context.get('address_instance', None)
        exist_address = CustomerAddress.objects.filter(customer=customer, alias=data['alias'],
                                                       status__slug_name="active").exists()
        if exist_address and not address_instance:
            raise serializers.ValidationError(
                {'detail': 'Ya se encuentra registrado una dirección con ese alias'},
                code='address_exist')
        elif exist_address and address_instance and address_instance.alias != data['alias']:
            raise serializers.ValidationError(
                {'detail': 'Ya se encuentra registrado una dirección con ese alias'},
                code='address_exist')

        point = data.pop('point', None)
        if point:
            data['point'] = Point(x=point['lng'], y=point['lat'], srid=4326)

        data['customer'] = customer
        return data

    def create(self, data):
        try:
            address = CustomerAddress.objects.create(**data)
            return address
        except Exception as ex:
            raise serializers.ValidationError({'detail': ex.args.__str__()})

    def update(self, instance, data):
        try:
            response = super().update(instance, data)
            return instance
        except Exception as ex:
            raise serializers.ValidationError({'detail': ex.args.__str__()})
