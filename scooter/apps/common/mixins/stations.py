from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
# Models
from scooter.apps.stations.models import Station
# django
from django.http import Http404, JsonResponse


class AddStationMixin(viewsets.GenericViewSet):
    """Add station mixin

    Manages adding a station object to views
    that require it.
    """
    station = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that the station exists."""
        pk = kwargs['station_id']
        try:
            self.station = get_object_or_404(Station, id=pk)
        except Http404:
            error = {'field': 'detail', 'message': 'No se encontro la central'}
            return JsonResponse(data={'errors': error, 'status': 'false'}, status=status.HTTP_404_NOT_FOUND)
        return super(AddStationMixin, self).dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        """ Add station to serializer context """
        context = super(AddStationMixin, self).get_serializer_context()
        context['station'] = self.station
        return context
