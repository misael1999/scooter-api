from rest_framework import serializers

from scooter.apps.promotions.models import MerchantPromotionType, MerchantPromotionRule, MerchantPromotion, \
    MerchantPromotionTimeInterval, MerchantPromotionTimeScheduleInterval


class CreateMerchantPromotionRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = MerchantPromotionRule
        fields = (
            'is_periodic',
            'has_limit_usage',
            'is_discount_percentage',
            'is_coupon_code',
            'minimum_order_price',
            'discount_amount',
            'usage_limit',
            'budget'
        )


class MerchantPromotionIntervalSerializer(serializers.ModelSerializer):

    class Meta:
        model = MerchantPromotionTimeInterval
        fields = (
            'from_time',
            'to_time'
        )

    def validate(self, data):
        from_time = data['from_time']
        to_time = data['to_time']
        if from_time <= to_time:
            raise serializers.ValidationError("La hora en que inicia no puede ser menor"
                                              " o igual a la hora en la que termina ")


class CreateScheduleIntervalSerializer(serializers.ModelSerializer):

    class Meta:
        model = MerchantPromotionTimeScheduleInterval
        fields = (
            'schedule',
        )


class CreateMerchantPromotion(serializers.ModelSerializer):
    promotion_rule = CreateMerchantPromotionRuleSerializer(required=True)
    time_intervals = MerchantPromotionIntervalSerializer(many=True, required=True)

    class Meta:
        model = MerchantPromotion
        fields = (
             'name',
             'description',
             'from_date',
             'to_date',
             'promotion_type'
         )

    def rule_validate(self, type_slug_name, promotion):
        is_valid = True
        rule = promotion['promotion_rule']
        # Validaciones cuando la promo NO es periodica
        if not rule['is_periodic']:
            # Debe de mandar desde y hasta la fecha
            if not promotion['from_date'] or not promotion['to_date']:
                raise ValueError('Debes ingresar desde y hasta que fecha se termina la promoción')
            if not rule['has_limit_usage'] and not rule['budget']:
                raise ValueError('Debes ingresar un presupuesto')
            if rule['has_limit_usage'] and not rule['usage_limit']:
                raise ValueError('Debes ingresar cuanto es el limite de uso')

        # validate data by promotion type
        return is_valid

    def create(self, data):
        try:
            # Validar regla de promoción
            promotion_type = data['promotion_type']
            is_valid = self.rule_validate(type_slug_name=promotion_type.slug_name, promotion=data)

            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al consultar precio de la orden'})
