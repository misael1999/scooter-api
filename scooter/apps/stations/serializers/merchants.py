from rest_framework import serializers


class UpdateMerchantStationSerializer(serializers.Serializer):
    has_rate_operating = serializers.BooleanField(required=False)
    increment_price_operating = serializers.FloatField(required=False)

    def update(self, merchant, data):
        try:
            for field, value in data.items():
                setattr(merchant, field, value)
            merchant.save()
            # import pdb; pdb.set_trace()
            return merchant
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception save general info, please check it")
            print(ex.args.__str__())
            raise ValueError(str(ex))