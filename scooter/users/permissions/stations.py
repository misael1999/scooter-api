
# Django rest framework
from rest_framework.permissions import BasePermission
from scooter.users.models import User


class IsAccountOwnerStation(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == view.station.user



