from rest_framework import serializers

from scooter.apps.common.models import Area


class AreaModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        geo_field = 'poly'
        fields = ('id',
                  'name',
                  'description',
                  'poly'
                  )
        read_only_fields = fields
