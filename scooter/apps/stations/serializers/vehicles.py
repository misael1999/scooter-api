""" Vehicles serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.common.models import TypeVehicle
from scooter.apps.stations.models import Vehicle
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer

# Serializers


class VehicleModelSerializer(ScooterModelSerializer):
    type_vehicle_id = serializers.PrimaryKeyRelatedField(queryset=TypeVehicle.objects.all(), source="type_vehicle")

    class Meta:
        model = Vehicle
        fields = ("id", "type_vehicle_id", "alias", "model", "year", "plate", "station", "status")
        read_only_fields = ('station', "id", "status")

    def validate(self, data):
        station = self.context['station']
        # Send instance of vehicle for validate of name not exist
        vehicle_instance = self.context.get('vehicle_instance', None)
        exist_vehicle = Vehicle.objects.filter(station=station, alias=data['alias'], status__slug_name="active").exists()
        if exist_vehicle and not vehicle_instance:
            raise serializers.ValidationError(
                {'detail': 'Ya se encuentra registrado un vehiculo con ese alias'},
                code='vehicle_exist')
        # When is update
        elif exist_vehicle and vehicle_instance and vehicle_instance.alias != data['alias']:
            raise serializers.ValidationError(
                {'detail': 'Ya se encuentra registrado un vehiculo con ese alias'},
                code='vehicle_exist')

        data['station'] = station
        return data
