""" Merchants serializers """
# Django rest framework
from rest_framework import serializers
# Models
from scooter.apps.orders.models import Order
from scooter.apps.orders.serializers.v2 import OrderWithoutInfoSerializer


class SummarySalesSerializer(serializers.Serializer):

    def update(self, merchant, data):
        try:
            request = self.context['request']
            month = request.query_params.get('month', 1)
            orders = merchant.order_set.filter(date_delivered_order__month=month, order_status__slug_name="delivered")
            commissions = 0
            if merchant.have_rate:
                commissions = len(orders) * merchant.rate

            total_sales = sum(order.order_price for order in orders)

            data_resp = {
                'orders': OrderWithoutInfoSerializer(orders, many=True).data,
                'total_orders': len(orders),
                'total_sales': total_sales,
                'profits': total_sales - commissions,
                'total_commissions': commissions
            }

            return data_resp
        except ValueError as ex:
            raise serializers.ValidationError({'detail': str(ex)})
        except Exception as e:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error desconocido'})
