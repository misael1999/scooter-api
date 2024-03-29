# Django rest
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Models
from scooter.apps.common.models import Area
# Viewset
from scooter.apps.common.serializers import TestPolygonSerializer
from scooter.apps.stations.models import StationZone, Station
from scooter.apps.stations.serializers import StationZoneSerializer, StationZoneSimpleSerializer
from scooter.utils.viewsets.scooter import ScooterViewSet
# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny


class ZonesViewSet(ScooterViewSet, mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):
    """ View set to check the zones """

    serializer_class = StationZoneSerializer()
    queryset = StationZone.objects.all()
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['POST'])
    def test_polygon(self, request, *args, **kwargs):
        serializer = TestPolygonSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(data=obj, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    def check_location(self, request, *args, **kwargs):
        try:
            station = Station.objects.get(pk=1)
            area_id = 1
            current_hour = timezone.localtime(timezone.now()).strftime('%H:%M:%S')
            # return Response({
            #     'status': False,
            #     'type': 0,
            #     'zone': {},
            #     'area_id': area_id,
            #     'station_phone_number': station.phone_number,
            #     'station_id': station.id,
            #     'message': 'No estaremos disponibles el día 31 de diciembre y
            #     01 de enero\nLos Pedidos les desea un feliz año nuevo, nos vemos pronto.'
            # }, status=status.HTTP_200_OK)

            lat = request.query_params.get('lat', 18.462938)
            lng = request.query_params.get('lng', -97.392701)
            point = Point(x=float(lng), y=float(lat), srid=4326)
            station = Station.objects.get(pk=1)
            areas = Area.objects.filter(poly__contains=point)
            area_id = 0
            current_hour = timezone.localtime(timezone.now()).strftime('%H:%M:%S')
            # Verificar si hay cobertura en su area
            if len(areas) == 0:
                return Response({
                    'status': False,
                    'type': 1,
                    'zone': {},
                    'area': area_id,
                    'station_id': station.id,
                    'station_phone_number': station.phone_number,
                    'message': 'En tu zona no hay servicios de restaurantes o supermercados'
                }, status=status.HTTP_200_OK)
            area_id = areas.last().id
            # Verificar si aun hay servicio disponible en el horario de la central
            if current_hour >= str(station.open_to) and current_hour <= str(station.close_to):
                pass
            else:
                message = 'La central de repartos no tiene servicio \n' \
                          ' abre: {} y cierra a las {}'.format(station.open_to, station.close_to)
                return Response({
                    'status': False,
                    'zone': {},
                    'type': 2,
                    'area': area_id,
                    'station_id': station.id,
                    'station_phone_number': station.phone_number,
                    'message': message
                }, status=status.HTTP_200_OK)

            # Verificar si esta activada las zonas restringidas
            if station.restricted_zones_activated:
                zones = station.stationzone_set.filter(type__slug_name="restricted_zone", poly__contains=point)
                # Si hay un punto en esa zona restringida, entonces regresamos una respuesta
                if len(zones) > 0:
                    zone = zones.last()
                    if zone.has_schedule:
                        # Si la zona tiene horario entonces verificamos la hora actual
                        if str(zone.from_hour) <= current_hour:
                            message = 'Te encuentras en una zona restringida por horarios \n' \
                                      ' nuestros repartidores no operan a' \
                                      ' partir de las {}'.format(zone.from_hour)
                            return Response({
                                'status': False,
                                'zone': StationZoneSimpleSerializer(zone).data,
                                'type': 2,
                                'area_id': area_id,
                                'station_id': station.id,
                                'station_phone_number': station.phone_number,
                                'message': message
                            }, status=status.HTTP_200_OK)
                    else:
                        # Es una zona sin cobertura
                        message = 'Te encuentras en una zona roja,' \
                                  ' ampliamos nuestra cobertura de manera constante.' \
                                  ' Vuelve a consultar la app más adelante.'
                        return Response({
                            'status': False,
                            'zone': StationZoneSimpleSerializer(zone).data,
                            'type': 2,
                            'area_id': area_id,
                            'station_id': station.id,
                            'station_phone_number': station.phone_number,
                            'message': message
                        }, status=status.HTTP_200_OK)

            return Response({
                'status': True,
                'type': 0,
                'area_id': area_id,
                'station_id': station.id,
                'station_phone_number': station.phone_number,
                'message': 'Si hay cobertura'
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            print(e.__str__())
            error = self.set_error_response(status=False, message="Error al revisar la ubicación", field="detail")
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            print(ex.__str__())
            error = self.set_error_response(status=False, message="Error al revisar la ubicación", field="detail")
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
