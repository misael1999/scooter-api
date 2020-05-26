""" Customers serializers """
# Django
# Django rest framework
# Models
from scooter.apps.customers.models import CustomerAddress
# Serializers
from scooter.utils.serializers.scooter import ScooterModelSerializer


class CustomerAddressModelSerializer(ScooterModelSerializer):

    class Meta:
        model = CustomerAddress
        fields = ("alias", "street", "suburb",
                  "postal_code", "exterior_number",
                  "inside_number", "reference", "point", "status")