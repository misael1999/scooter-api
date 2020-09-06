# Django rest
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

from scooter.apps.marketing.models import Marketer
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Serializers
from scooter.apps.marketing.serializers import MarketerUserSimpleSerializer, MarketerSignUpSerializer
# Filters


class MarketerViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.UpdateModelMixin):
    """ Handle signup and update of merchant """
    queryset = Marketer.objects.all()
    serializer_class = MarketerUserSimpleSerializer
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        """ Marketer sign up """
        serializer = MarketerSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = self.set_response(status='ok',
                                 data={},
                                 message='Se ha registrado un nuevo miembro de marketing')
        return Response(data, status=status.HTTP_201_CREATED)
