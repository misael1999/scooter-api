
# Django rest framework
from rest_framework.permissions import BasePermission

from scooter.apps.delivery_men.models import DeliveryMan


class IsSameDeliveryMan(BasePermission):

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_object()
        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """ Verify delivery man is the same that in the obj """
        try:
            delivery_man = request.user.deliveryman
            is_active = delivery_man.status.slug_name == 'active'
            return obj == delivery_man and is_active
        except DeliveryMan.DoesNotExist:
            return False


class IsAccountOwnerDeliveryMan(BasePermission):

    def has_permission(self, request, view):
        """Verify user have a delivery man."""
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



