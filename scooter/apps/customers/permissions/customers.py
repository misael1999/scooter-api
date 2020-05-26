
# Django rest framework
from rest_framework.permissions import BasePermission


class IsAccountOwnerCustomer(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == view.customer.user



