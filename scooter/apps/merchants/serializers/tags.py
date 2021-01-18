""" Common status serializers """
# Django rest framework
from rest_framework import serializers
# Models
from rest_framework.validators import UniqueValidator

from scooter.apps.common.serializers import Base64ImageField
from scooter.apps.merchants.models.tags import MerchantTag, Tag
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer


class TagModelSerializer(ScooterModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class TagModelSimpleSerializer(ScooterModelSerializer):
    picture = Base64ImageField(allow_null=True, allow_empty_file=True, required=False)

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'picture',
            'area'
        )
        read_only_fields = fields


class MerchantTagModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = MerchantTag
        fields = '__all__'
        read_only_fields = ('id', 'tag_name')

    def create(self, data):
        try:
            tag = data['tag']
            data["tag_name"] = tag.name
            return super().create(data)
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create product, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error registrar el metodo de pago en el comercio'})

    def update(self, tag, data):
        picture = data['picture']
        if picture:
            tag.picture.delete()
        return super(MerchantTagModelSerializer, self).update(tag, data)
