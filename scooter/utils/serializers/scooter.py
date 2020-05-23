from rest_framework.serializers import ModelSerializer
# Serializers
from scooter.apps.common.serializers.status import StatusModelSerializer


# Serializer with status object
class ScooterModelSerializer(ModelSerializer):
    status = StatusModelSerializer(read_only=True)
