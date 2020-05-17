# Django rest
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
# Custom viewset
from scooter.utils.viewsets import EcommerceViewSet
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
# Models
from scooter.common.models.status import Status
# Serializers
from scooter.common.serializers.status import (StatusModelSerializer,)


class StatusViewSet(EcommerceViewSet):
    """ Return status"""
    lookup_field = 'id'
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False, url_path="status")
    def status(self, request, *args, **kwargs):
        query = Status.objects.all()
        sale_status = StatusModelSerializer(query, many=True).data
        data = self.set_response(status='ok', data=sale_status, message='Estatus generales')
        return Response(data=data, status=status.HTTP_200_OK)



