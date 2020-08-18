# Rest framework
from rest_framework import serializers
# Models
from scooter.apps.customers.serializers import CustomerSimpleModelSerializer
from scooter.apps.merchants.models import MemberMerchant


class MembersMerchantModelSerializer(serializers.ModelSerializer):
    customer = CustomerSimpleModelSerializer(read_only=True)

    class Meta:
        model = MemberMerchant
        fields = ("id",
                  "merchant",
                  "customer",
                  "total_orders",
                  "total_orders_cancelled",
                  "first_order_date",
                  "last_order_date")
        read_only_fields = fields
