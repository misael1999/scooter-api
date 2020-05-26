
# Django rest framework
from rest_framework.permissions import BasePermission


class IsAccountOwnerStation(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == view.station.user



