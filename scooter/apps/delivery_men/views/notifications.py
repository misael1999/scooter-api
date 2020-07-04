# Django rest
from rest_framework import mixins, status
# Models
from scooter.apps.common.models import Notification
# Serializers
from scooter.apps.common.serializers import NotificationModelSerializer
# Viewset
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins import AddDeliveryManMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.delivery_men.permissions import IsAccountOwnerDeliveryMan
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class NotificationDeliveryManViewSet(ScooterViewSet,
                                     mixins.ListModelMixin, AddDeliveryManMixin):
    serializer_class = NotificationModelSerializer
    queryset = Notification.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerDeliveryMan)

    """ Method dispatch in AddCustomerMixin """
    delivery_man = None

    def get_queryset(self):
        # user = request['user']
        return self.delivery_man.user.notifications.all()
