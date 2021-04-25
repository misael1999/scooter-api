from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, Point
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


class TestPolygonSerializer(serializers.Serializer):

    geojson_data = serializers.CharField()

    def create(self, data):
        try:
            # Get coordinates
            geojson_data = data.get('geojson_data', None)
            # poly = get_coordinates(geojson_data=geojson_data)
            poly = GEOSGeometry(geojson_data)
            lat = 19.0415234
            lng = -98.2007795

            point = Point(x=float(lng), y=float(lat), srid=4326)
            elements = poly.contains(point)
            import pdb; pdb.set_trace()
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in station zone serializer, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al crear una nueva zona'})

#
# def get_coordinates(geojson_data):
#     try:
#         return poly
#     except ValueError as e:
#         raise ValueError(e)
#     except Exception as ex:
#         print("Exception in get coordinates, please check it")
#         print(ex.args.__str__())
#         raise ValueError('Error al obtener las coordenadas')