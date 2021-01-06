from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from scooter.apps.common.mixins import AddSupportMixin
from scooter.apps.support.serializers import SupportMessageSimpleSerializer, CreateMessageSupportSerializer
from scooter.utils.viewsets import ScooterViewSet


class SupportMessageViewSet(ScooterViewSet, AddSupportMixin, mixins.ListModelMixin, mixins.CreateModelMixin):
    serializer_class = SupportMessageSimpleSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering = ('created',)
    ordering_fields = ('created',)
    # filter_fields = ('status',)
    permission_classes = (IsAuthenticated,)
    support = None

    def get_queryset(self):
        return self.support.messages.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateMessageSupportSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = CreateMessageSupportSerializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        return Response(data=message, status=status.HTTP_201_CREATED)
