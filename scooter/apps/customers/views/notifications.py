# Django rest
from rest_framework import mixins, status
# Models
from scooter.apps.common.models import Notification
from scooter.apps.customers.models.customers import CustomerAddress
# Serializers
from scooter.apps.common.serializers import NotificationModelSerializer

# Viewset
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins.customers import AddCustomerMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.customers.permissions import IsAccountOwnerCustomer
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class NotificationCustomerViewSet(ScooterViewSet,
                                  mixins.ListModelMixin, AddCustomerMixin):

    serializer_class = NotificationModelSerializer
    queryset = Notification.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerCustomer)

    """ Method dispatch in AddCustomerMixin """
    customer = None

    def get_queryset(self):
        # user = request['user']
        return self.customer.user.notifications.all()
