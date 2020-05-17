
# Django rest framework
from rest_framework.permissions import BasePermission
from scooter.users.models import User


class IsAccountOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user



