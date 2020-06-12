from rest_framework import serializers


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
