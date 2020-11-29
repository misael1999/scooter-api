""" Vehicles serializers """
# Django rest framework
import base64
import tempfile
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, WKTWriter, Point
from django.utils import timezone
from rest_framework import serializers
# Models
from rest_framework.validators import UniqueValidator

from scooter.apps.common.models import TypeVehicle, os
from scooter.apps.merchants.models import Branch
from scooter.apps.stations.models import Vehicle, StationZone
# Utilities
from scooter.apps.stations.serializers import PointSerializer
from scooter.apps.users.models import User
from scooter.utils.serializers.scooter import ScooterModelSerializer


class BranchSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationZone
        geo_field = 'location'
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=20)
    point = PointSerializer()

    class Meta:
        geo_field = 'location'
        model = Branch
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BranchSerializer, self).__init__(*args, **kwargs)
        merchant = self.context.get('merchant', None)
        if merchant:
            self.fields['name'].validators[0].queryset = Branch.objects.filter(merchant=merchant)

    def create(self, data):
        try:
            user = User(username=data.pop('username'),
                        is_verified=True,
                        role=User.BRANCH,
                        is_client=False,
                        verification_deadline=timezone.localtime(timezone.now()))

            password = data.pop('password')
            user.set_password(password)
            user.save()
            data_point = data.pop('point', None)
            point = Point(x=data_point['lng'], y=data_point['lat'])

            branch = Branch.objects.create(**data,
                                           location=point,
                                           user=user)
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in station zone serializer, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al crear una nueva zona'})

    def update(self, branch, data):
        try:
            point = data.pop('point', None)
            username = data.pop('username', None)
            password = data.pop('password', None)
            if point:
                branch.location = point
                branch.save()
            return super().update(branch, data)
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in update station zone serializer, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al actualizar la zona'})
