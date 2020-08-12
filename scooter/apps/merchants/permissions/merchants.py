
# Django rest framework
from rest_framework.permissions import BasePermission
# Models
from scooter.apps.merchants.models import Merchant


class IsAccountOwnerMerchant(BasePermission):
    """Verify requesting user is the merchant."""

    def has_permission(self, request, view):
        """Verify user have a merchant."""
        user = request.user

        # Station
        return user.id == view.merchant.user_id



