from rest_framework import serializers
# Models
from scooter.apps.common.models import TypeAddress


class TypeAddressModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = TypeAddress
        fields = ('id', 'name', 'slug_name')
        read_only_fields = ('id', 'name', 'slug_name')


# Convert to base 64
class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension,)
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


# Serializer to rename the image and verify it is image
class ImageColorSerializer(serializers.Serializer):
    file = Base64ImageField(max_length=None, use_url=True)


# Overload the get_queryset method, using the station information from the context:
class StationFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        station = self.context.get('station', None)
        queryset = super(StationFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not station or not queryset:
            return None
        return queryset.filter(station=station)


class CustomerFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        customer = self.context.get('customer', None)
        queryset = super(CustomerFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not customer or not queryset:
            return None
        return queryset.filter(customer=customer)


class MerchantFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        merchant = self.context.get('merchant', None)
        queryset = super(MerchantFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not merchant or not queryset:
            return None
        return queryset.filter(merchant=merchant)


class CurrentCustomUserDefault(object):
    user_id = None

    def set_context(self, serializer_field):
        self.user_id = serializer_field.context['request'].user.id

    def __call__(self):
        return self.user_id

    def __repr__(self):
        return '%s()' % self.__class__.__name__
