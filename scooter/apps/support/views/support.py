from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from scooter.apps.common.mixins import AddSupportMixin
from scooter.apps.support.serializers import SupportMessageSimpleSerializer, CreateMessageSupportSerializer
from scooter.utils.viewsets import ScooterViewSet


class SupportMessageViewSet(ScooterViewSet, AddSupportMixin, mixins.ListModelMixin, mixins.CreateModelMixin):
    serializer_class = SupportMessageSimpleSerializer
    permission_classes = (IsAuthenticated,)
    support = None

    def get_queryset(self):
        return self.support.messages.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateMessageSupportSerializer
        return self.serializer_class
