
# Django rest framework
from rest_framework.permissions import BasePermission
# Models
from scooter.apps.stations.models import Station


class IsAccountOwnerStation(BasePermission):
    """Verify requesting user is the station created."""

    def has_permission(self, request, view):
        """Verify user have a station."""
        try:
            # Station coming to token
            station = request.user.station
        except Station.DoesNotExist:
            return False
        # Station
        return station == view.station



