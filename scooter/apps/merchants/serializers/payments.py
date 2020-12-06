""" Common status serializers """
# Django rest framework
from rest_framework import serializers
# Models
from rest_framework.validators import UniqueValidator

from scooter.apps.merchants.models.payments import MerchantPaymentMethod
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer


class MerchantPaymentMethodSimpleSerializer(ScooterModelSerializer):

    class Meta:
        model = MerchantPaymentMethod
        fields = '__all__'


class MerchantPaymentMethodModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = MerchantPaymentMethod
        fields = '__all__'

    def create(self, data):
        try:
            payment_method = data['payment_method']
            data['name'] = payment_method.name
            return super().create(data)
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create product, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error registrar el metodo de pago en el comercio'})
