from rest_framework import serializers

from scooter.apps.common.models import Schedule
from scooter.apps.promotions.models import MerchantPromotionType, MerchantPromotionRule, MerchantPromotion, \
    MerchantPromotionTimeInterval, MerchantPromotionTimeScheduleInterval


class ScheduleIntervalSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantPromotionTimeScheduleInterval
        fields = (
            'id',
            'schedule',
            'schedule_name',
            'schedule_slug_name',
        )
        read_only_fields = fields


class MerchantPromotionIntervalSimpleSerializer(serializers.ModelSerializer):

    schedules = ScheduleIntervalSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = MerchantPromotionTimeInterval
        fields = (
            'id',
            'from_time',
            'to_time',
            'schedules'
        )
        read_only_fields = fields


class MerchantPromotionRuleSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = MerchantPromotionRule
        fields = (
            'id',
            'is_periodic',
            'has_limit_usage',
            'has_limit_discount_amount',
            'is_discount_percentage',
            'is_coupon_code',
            'minimum_order_price',
            'discount_amount',
            'limit_discount_amount',
            'usage_limit',
            'budget'
        )
        read_only_fields = fields


class MerchantPromotionSimpleSerializer(serializers.ModelSerializer):

    rule = MerchantPromotionRuleSimpleSerializer(read_only=True)
    time_intervals = MerchantPromotionIntervalSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = MerchantPromotion
        fields = (
            'id',
            'name',
            'description',
            'from_date',
            'to_date',
            'promotion_type',
            'rule',
            'time_intervals'
        )
        read_only_fields = fields


# Serialiers para crear promociones
# ==================================

class CreateMerchantPromotionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantPromotionRule
        fields = (
            'is_periodic',
            'has_limit_usage',
            'has_limit_discount_amount',
            'is_discount_percentage',
            'is_coupon_code',
            'minimum_order_price',
            'discount_amount',
            'limit_discount_amount',
            'usage_limit',
            'budget'
        )


class CreateMerchantPromotionIntervalSerializer(serializers.ModelSerializer):
    schedule_ids = serializers.PrimaryKeyRelatedField(many=True,
                                                      queryset=Schedule.objects.all())

    class Meta:
        model = MerchantPromotionTimeInterval
        fields = (
            'from_time',
            'to_time',
            'schedule_ids'
        )

    def validate(self, data):
        from_time = data['from_time']
        to_time = data['to_time']
        if from_time >= to_time:
            raise serializers.ValidationError("La hora en que inicia no puede ser mayor"
                                              " o igual a la hora en la que termina ")
        return data


class CreateMerchantPromotion(serializers.ModelSerializer):
    promotion_rule = CreateMerchantPromotionRuleSerializer(required=True)
    time_intervals = CreateMerchantPromotionIntervalSerializer(many=True, required=True)

    class Meta:
        model = MerchantPromotion
        fields = (
            'name',
            'description',
            'from_date',
            'to_date',
            'promotion_type',
            'promotion_rule',
            'time_intervals'
        )

    def validate(self, data):
        # Check if exist promotion active
        merchant = self.context['merchant']
        promotion_exist = MerchantPromotion.objects.filter(merchant=merchant,
                                                           promotion_type=data['promotion_type'],
                                                           status_id=1)
        if promotion_exist.exists():
            raise serializers.ValidationError("Ya existe una promoción activa o en proceso de revisión")
        return data

    def create(self, data):
        try:
            # Validar regla de promoción
            promotion_type = data.get('promotion_type', None)
            self.rule_validate(type_slug_name=promotion_type.slug_name, promotion=data)
            rule = data.pop('promotion_rule', None)
            time_intervals = data.pop('time_intervals', [])

            # Guardar datos de la promoción
            data = self.get_data_by_promotion_type(type_slug_name=promotion_type.slug_name, data=data)
            promotion = MerchantPromotion.objects.create(**data,
                                                         merchant=self.context['merchant'],
                                                         station_id=1)
            # Crear regla
            MerchantPromotionRule.objects.create(**rule,
                                                 merchant_promotion=promotion)
            # Crear intervalos de tiempo
            self.save_time_intervals(time_intervals=time_intervals, promotion=promotion)

            return promotion
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create promotion, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al crear una promoción'})

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

    def save_time_intervals(self, time_intervals, promotion):
        interval_schedule_to_save = []
        for interval in time_intervals:
            schedules = interval.pop('schedule_ids', [])
            promotion_interval = MerchantPromotionTimeInterval.objects.create(**interval,
                                                                              promotion=promotion)
            for schedule in schedules:
                interval_schedule_to_save.append(
                    MerchantPromotionTimeScheduleInterval(promotion_interval=promotion_interval,
                                                          schedule=schedule,
                                                          schedule_name=schedule.name,
                                                          schedule_slug_name=schedule.slug_name))

        MerchantPromotionTimeScheduleInterval.objects.bulk_create(interval_schedule_to_save)
        return True

    def get_data_by_promotion_type(self, type_slug_name, data):

        sw_purchase = {
            'delivery_discount': {
                "name": 'Entrega con descuentos en el costo de envio o envio gratuito',
                "description": 'Con esta promoción puedes cubrir el costo envio o se hace un descuento al cliente'
            },
            'default': {
                "name": data['name'],
                "description": data['description']
            }
        }

        info = sw_purchase.get(type_slug_name, 'default')
        data['name'] = info['name']
        data['description'] = info['description']
        return data
