from fcm_django.models import FCMDevice
from rest_framework import serializers


class DeleteDeviceSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=400)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, data):
        try:
            FCMDevice.objects.filter(user=data['user'], registration_id=data['token']).delete()
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in delete device, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al eliminar token'})
