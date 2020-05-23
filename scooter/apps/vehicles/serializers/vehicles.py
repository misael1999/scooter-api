""" Vehicles serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.vehicles.models import Vehicle
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer

# Serializers


class VehicleModelSerializer(ScooterModelSerializer):
    class Meta:
        model = Vehicle
        fields = ("id", "alias", "model", "year", "plate", "station", "status")
        read_only_fields = ('station', "id")

    def validate(self, data):
        station = self.context['station']
        # Send instance of vehicle for validate of name not exist
        vehicle_instance = self.context.get('vehicle_instance', None)
        exist_vehicle = Vehicle.objects.filter(station=station, alias=data['alias'], status__slug_name="active").exists()
        if exist_vehicle and not vehicle_instance:
            raise serializers.ValidationError(
                {'detail': 'Ya se encuentra registrado un vehiculo con ese alias'},
                code='vehicle_exist')
        elif exist_vehicle and vehicle_instance and vehicle_instance.alias != data['alias']:
            raise serializers.ValidationError(
                {'detail': 'Ya se encuentra registrado un vehiculo con ese alias'},
                code='vehicle_exist')

        data['station'] = station
        return data
