# Rest framework
from rest_framework import serializers
# Models
from scooter.apps.stations.models import MemberStation


class MembersStationModelSerializer(serializers.ModelSerializer):

    customer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = MemberStation
        fields = ("id",
                  "station",
                  "customer",
                  "total_orders",
                  "total_orders_cancelled",
                  "first_order_date",
                  "last_order_date")
        read_only_fields = fields
