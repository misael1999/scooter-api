# Django rest
from rest_framework import mixins, status
# Models
from scooter.apps.common.models import Notification
# Serializers
from scooter.apps.common.serializers import NotificationModelSerializer

# Viewset
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins import AddStationMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.stations.permissions import IsAccountOwnerStation
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class NotificationStationViewSet(ScooterViewSet,
                                 mixins.ListModelMixin, AddStationMixin):
    serializer_class = NotificationModelSerializer
    queryset = Notification.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerStation)

    """ Method dispatch in AddCustomerMixin """
    station = None

    def get_queryset(self):
        # user = request['user']
        return self.station.user.notifications.all()
