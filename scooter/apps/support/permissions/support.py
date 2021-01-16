from rest_framework.permissions import BasePermission

from scooter.apps.support.models import Support


class IsStationOrOwnerCustomer(BasePermission):
    """Verify requesting user is the station created."""

    def has_permission(self, request, view):
        """Verify user have a station."""
        try:
            support = view.support
            user = request.user
            return user.is_station() or support.user_id == user.id
        except Support.DoesNotExist:
            return False
