# Django rest
from rest_framework.response import Response
# Mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from scooter.apps.common.mixins import AddStationMixin
# Permissions
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from scooter.apps.stations.permissions import IsAccountOwnerStation
# Utilities
from scooter.apps.support.serializers import (SupportModelSimpleSerializer,
                                              CreateSupportModelSerializer)
from scooter.utils.viewsets import ScooterViewSet


class StationSupportViewSet(ScooterViewSet, mixins.ListModelMixin,
                            mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                            AddStationMixin):
    """ Handler support open """
    permission_classes = (IsAuthenticated, IsAccountOwnerStation)
    serializer_class = SupportModelSimpleSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering = ('-created',)
    filter_fields = ('status',)
    lookup_field = 'id'
    station = None

    def get_queryset(self):
        if self.action in ['list', 'update', 'partial_update', 'retrieve']:
            return self.station.support_set.all()
        return self.queryset

    def get_serializer_class(self):
        if self.action in ['create']:
            return CreateSupportModelSerializer
        return self.serializer_class

    def get_serializer_context(self):
        """ Add if is customer to serializer context """
        context = super(StationSupportViewSet, self).get_serializer_context()
        context['is_customer'] = False
        return context

    def create(self, request, *args, **kwargs):
        serializer = CreateSupportModelSerializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        support = serializer.save()

        return Response(data=support, status=status.HTTP_201_CREATED)
