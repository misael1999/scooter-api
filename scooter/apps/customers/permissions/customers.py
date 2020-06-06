# Django rest framework
from rest_framework.permissions import BasePermission
from scooter.apps.customers.models import Customer


class IsAccountOwnerCustomer(BasePermission):

    def has_permission(self, request, view):
        """Verify user have a customer."""
        try:
            # Customer coming to token
            customer = request.user.customer
        except Customer.DoesNotExist:
            return False
        # Customer
        return customer == view.customer




