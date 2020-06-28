
"""Orders permissions."""

# Django REST Framework
from rest_framework.permissions import BasePermission

from scooter.apps.delivery_men.models import DeliveryMan


class IsOrderStationOwner(BasePermission):
    """Verify requesting station is the order create."""

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_object()
        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Verify requesting station is the order creator."""
        return view.station == obj.station


class IsOrderDeliveryManStationOwner(BasePermission):
    """Verify requesting delivery man is the station order create."""

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_object()
        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Verify requesting delivery man is the station order creator."""
        return view.delivery_man.station == obj.station


class IsOrderDeliveryManOwner(BasePermission):
    """Verify requesting delivery man is the station order create."""

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_object()
        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Verify requesting delivery man is the station order creator."""
        try:
            return view.delivery_man == obj.delivery_man
        except DeliveryMan.DoesNotExist:
            return False

