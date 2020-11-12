""" Vehicles serializers """
# Django rest framework
import base64
import tempfile
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, WKTWriter
from rest_framework import serializers
# Models
from rest_framework.validators import UniqueValidator

from scooter.apps.common.models import TypeVehicle, os
from scooter.apps.stations.models import Vehicle, StationZone
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer


class StationZoneSerializer(serializers.ModelSerializer):

    kml_file = serializers.FileField(required=False)
    station = serializers.HiddenField(default=1)
    type_id = serializers.IntegerField()
    type = serializers.StringRelatedField()
    name = serializers.CharField(max_length=70,
                                 validators=
                                 [UniqueValidator(
                                     queryset=None,
                                     message='Ya existe una zona con ese nombre')])

    class Meta:
        geo_field = 'poly'
        model = StationZone
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(StationZoneSerializer, self).__init__(*args, **kwargs)
        station = self.context.get('station', None)
        if station:
            self.fields['name'].validators[0].queryset = StationZone.objects.filter(station=station)

    def create(self, data):
        try:
            station = self.context['station']
            data.pop('station')
            # Get coordinates
            kml_file = data.pop('kml_file', None)
            tempfn = get_temp_file(kml_file=kml_file)

            poly = get_coordinates(kml_file=tempfn)
            zone = StationZone.objects.create(**data, station=station, poly=poly)
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in station zone serializer, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al crear una nueva zona'})

    def update(self, zone, data):
        try:
            kml_file = data.pop('kml_file', None)
            if kml_file:
                tempfn = get_temp_file(kml_file=kml_file)
                poly = get_coordinates(kml_file=tempfn)
                zone.poly = poly
                zone.save()
            return super().update(zone, data)
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in update station zone serializer, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al actualizar la zona'})


def get_temp_file(kml_file):
    tempf, tempfn = tempfile.mkstemp()
    try:
        for chunk in kml_file.chunks():
            os.write(tempf, chunk)
    except Exception as ex:
        raise Exception("Problem with the input file %s" % kml_file.name)
    finally:
        os.close(tempf)
    return tempfn


def get_coordinates(kml_file):
    try:

        wkt_w = WKTWriter()
        source = DataSource(kml_file)
        poly = None
        for layer in source:
            for feat in layer:
                # Get the feature geometry.
                geom = feat.geom
                poly = GEOSGeometry(wkt_w.write(geom.geos))

                # line = Line.objects.create(
                #     name=property['name'],
                #     description=property['description'],
                #     layer_name=feat.layer_name,
                #     # Make a GeosGeometry object
                #     geom=GEOSGeometry(wkt_w.write(geom.geos)),
                # )
        if not poly:
            raise ValueError('El archivo no tiene coordenadas')
        return poly
    except ValueError as e:
        raise ValueError(e)
    except Exception as ex:
        print("Exception in get coordinates, please check it")
        print(ex.args.__str__())
        raise ValueError('Error al obtener las coordenadas')