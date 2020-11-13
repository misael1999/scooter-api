# Django rest
from django.contrib.gis.geos import Point
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Models
from scooter.apps.common.models import Area
from scooter.apps.customers.models.customers import CustomerAddress
from scooter.apps.common.models.status import Status
# Serializers
from scooter.apps.customers.serializers.addresses import (CustomerAddressModelSerializer,
                                                          AddressRecommendationsSerializer)
# Viewset
from scooter.apps.stations.models import StationZone, Station
from scooter.apps.stations.serializers import StationZoneSerializer
from scooter.utils.viewsets.scooter import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class ZonesViewSet(ScooterViewSet, mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):
    """ View set to check the zones """

    serializer_class = StationZoneSerializer()
    queryset = StationZone.objects.all()
    permission_classes = (AllowAny,)

    # Filters
    # filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    # search_fields = ('alias', 'full_address', 'category')
    # # ordering_fields = ('created',)
    # # Affect the default order
    # ordering = ('-created', '-alias', '-category')
    # filter_fields = ('category',)

    @action(detail=False, methods=['GET'])
    def check_location(self):
        try:
            lat = self.request.query_params.get('lat', 18.462938)
            lng = self.request.query_params.get('lng', -97.392701)
            point = Point(x=float(lng), y=float(lat), srid=4326)
            station = Station.objects.first()
            areas = Area.objects.filter(poly__contains=point)
            # Verificar si hay cobertura en su area
            if len(areas) == 0:
                return Response({
                    'status': False,
                    'type': 1,
                    'message': 'Por el momento en tu zona no hay servicios de restaurantes o supermercados'
                }, status=status.HTTP_200_OK)
            # Verificar si esta activada las zonas restringidas
            if station.restricted_zones_activated:
                zones = station.stationzone_set.filter(type__slug_name="restricted_zone", poly__contains=point)
                # Si hay un punto en esa zona restringida, entonces regresamos una respuesta
                if zones.count() > 0:
                    return Response({
                        'status': False,
                        'zone': StationZoneSerializer(zones.last()).data,
                        'type': 2,
                        'message': 'Por el momento en tu zona no hay servicios de restaurantes o supermercados'
                    }, status=status.HTTP_200_OK)

            return Response({
                'status': True,
                'type': 0,
                'message': 'Si hay cobertura'
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            error = self.set_error_response(status=False, message="Error al revisar la ubicación", field="detail")
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error = self.set_error_response(status=False, message="Error al revisar la ubicación", field="detail")
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
