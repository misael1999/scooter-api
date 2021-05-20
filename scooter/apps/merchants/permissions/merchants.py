
# Django rest framework
from rest_framework.permissions import BasePermission
# Models
from scooter.apps.merchants.models import Merchant


class IsAccountOwnerMerchantOrStationAdmin(BasePermission):
    """Verify requesting user is the merchant."""

    def has_permission(self, request, view):
        """Verify user have a merchant."""
        user = request.user

        # Station
        return user.is_station() or user.id == view.merchant.user_id


class IsAccountOwnerMerchant(BasePermission):
    """Verify requesting user is the merchant."""

    def has_permission(self, request, view):
        """Verify user have a merchant."""
        user = request.user

        # Station
        return user.id == view.merchant.user_id


class IsProductOwner(BasePermission):

    def has_permission(self, request, view):
        """Verify user have a merchant."""
        user = request.user

        # Station
        return user.id == view.product.user_id


class IsSameMerchant(BasePermission):

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_object()
        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """ Verify delivery man is the same that in the obj """
        user = request.user
        return user.id == obj.user_id




