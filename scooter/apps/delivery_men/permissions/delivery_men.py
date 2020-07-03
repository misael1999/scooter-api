
# Django rest framework
from rest_framework.permissions import BasePermission

from scooter.apps.delivery_men.models import DeliveryMan


class IsAccountOwnerDeliveryMan(BasePermission):

    def has_permission(self, request, view):
        """Verify user have a customer."""
        try:
            # Customer coming to token
            delivery_man = request.user.deliveryman
        except DeliveryMan.DoesNotExist:
            return False
        # Customer
        return delivery_man == view.delivery_man


class IsActiveDeliveryMan(BasePermission):

    def has_permission(self, request, view):
        return view.delivery_man.status.slug_name == 'active'



