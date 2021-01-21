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

    picture = Base64ImageField(allow_null=True,
                               allow_empty_file=True,
                               required=False)

    class Meta:
        model = Tag
        fields = '__all__'

    def update(self, tag, data):
        picture = data['picture']
        if picture:
            tag.picture.delete()
        return super(TagModelSerializer, self).update(tag, data)


class TagModelSimpleSerializer(ScooterModelSerializer):

    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'picture',
            'area',
            'category',
            'category_id'
        )
        read_only_fields = fields


class CreateMerchantTagSerializer(serializers.Serializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.filter(status_id=1)
    )
    delete_tags = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=Tag.objects.filter(status_id=1)
    )

    def create(self, data):
        try:
            delete_tags = data.get('delete_tags', [])
            data['delete_tags'] = delete_tags
            tags = data['tags']
            merchant_tags_to_save = []
            merchant = self.context['merchant']
            for tag in tags:
                # Agregar nuevas tags al comercio
                try:
                    MerchantTag.objects.get(merchant=merchant, tag_id=tag.id)
                except MerchantTag.DoesNotExist:
                    merchant_tags_to_save.append(MerchantTag(merchant=merchant,
                                                             tag_id=tag.id,
                                                             tag_name=tag.name))

            for tag in delete_tags:
                # Eliminar tags
                try:
                    merchant_tag = MerchantTag.objects.get(merchant=merchant, tag_id=tag.id)
                    merchant_tag.delete()
                except MerchantTag.DoesNotExist:
                    pass
            MerchantTag.objects.bulk_create(merchant_tags_to_save)
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create merchant tag, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al asignar etiquetas al comercio'})


class MerchantTagSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantTag
        fields = (
            'id',
            'tag_id',
            'merchant',
            'tag_name'
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
            return super(MerchantTagModelSerializer, self).create(data)
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create product, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al registrar una nueva etiqueta'})

