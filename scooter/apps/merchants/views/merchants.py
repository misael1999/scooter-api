# Cache methods
import random

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
# Django rest
from django.contrib.gis.geos import Point
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters.rest_framework import DjangoFilterBackend
from ipython_genutils.py3compat import xrange
from rest_framework import status, mixins
from rest_framework.decorators import action
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from scooter.apps.common.models import CategoryMerchant, Area, Status
from scooter.apps.common.serializers import AreaModelSerializer
from scooter.apps.merchants.models import Merchant, Tag
# Permissions
from scooter.apps.merchants.permissions import IsSameMerchantOrStationAdmin
# Models
# Serializers
from scooter.apps.merchants.serializers import (MerchantWithAllInfoSerializer, UpdateInfoMerchantSerializer,
                                                AvailabilityMerchantSerializer, ChangePasswordMerchantSerializer,
                                                MerchantInfoSerializer, TagModelSimpleSerializer,
                                                MerchantRatingSerializer)
# Utilities
from scooter.apps.merchants.utils import MerchantTagFilter
from scooter.utils.viewsets import ScooterViewSet


class MerchantViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """ Handle signup and update of merchant """
    queryset = Merchant.objects.all()
    serializer_class = MerchantWithAllInfoSerializer
    lookup_field = 'id'
    # Filters
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('merchant_name',)
    ordering_fields = ('is_open', 'reputation', 'created')
    ordering = ('-is_open', 'created')
    filter_class = MerchantTagFilter

    def get_queryset(self):
        if self.action == 'list':
            merchants = Merchant.objects.filter(status=1, information_is_complete=True)
            return merchants
        return self.queryset

    # def filter_queryset(self, queryset):
    #     queryset = super(MerchantViewSet, self).filter_queryset(queryset=queryset)
    #     order_by = self.request.query_params.get('order_by', None)
    #     if order_by:
    #         if order_by == 'nearest':
    #             lat = self.request.query_params.get('lat', 18.462938)
    #             lng = self.request.query_params.get('lng', -97.392701)
    #             point = Point(x=float(lng), y=float(lat), srid=4326)
    #             queryset = queryset.annotate(distance=Distance('point', point)).order_by('-is_open', 'distance')
    #         else:
    #             queryset = queryset.order_by('-is_open', order_by, '-total_grades')
    #     return queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'retrieve':
            serializer_class = MerchantInfoSerializer
        if self.action in ['list']:
            serializer_class = MerchantWithAllInfoSerializer
        return serializer_class

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'home']:
            permission_classes = [AllowAny]
        elif self.action in ['partial_update', 'update', 'update_info']:
            permission_classes = [IsAuthenticated, IsSameMerchantOrStationAdmin]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    # def perform_destroy(self, instance):
    #     try:
    #         sts = Status.objects.get(slug_name='inactive')
    #         instance.status = sts
    #         instance.save()
    #     except Status.DoesNotExist:
    #         error = self.set_error_response(status=False, field='status',
    #                                         message='Ha ocurrido un error al borrar el vehiculo')
    #         return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['PATCH', 'PUT'])
    def unlock(self, request, *args, **kwargs):
        merchant = self.get_object()
        sts = Status.objects.get(slug_name='active')
        # Send instance of vehicle for validate of name not exist
        merchant.status = sts
        merchant.save()
        data = self.set_response(status=True, data={}, message="Comercio desbloqueado correctamente")
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=True, methods=('PATCH', 'PUT'))
    def update_info(self, request, *args, **kwargs):
        try:
            merchant = self.get_object()
            partial = request.method == 'PATCH'
            serializer = UpdateInfoMerchantSerializer(merchant, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = {}
        except Merchant.DoesNotExist:
            return Response(
                self.set_error_response(status=False, field='Detail', message='No existe el comercio'))
        return Response(self.set_response(status='ok', data=data, message='Información actualizada correctamente'))

    @action(detail=True, methods=['GET'])
    def area(self, request, *args, **kwargs):
        try:
            merchant = self.get_object()
            area = merchant.area
            data = AreaModelSerializer(area).data
            return Response(data, status=status.HTTP_200_OK)
        except Area.DoesNotExist:
            return Response(
                self.set_error_response(status=False, field='Detail', message='No existe el área'))
        except Exception as ex:
            return Response(
                self.set_error_response(status=False, field='Detail',
                                        message='Error al consultar el area en comercios'))

    @action(detail=True, methods=['GET'])
    def ratings(self, request, *args, **kwargs):
        merchant = self.get_object()
        ratings = merchant.ratingorder_set.all()
        data = MerchantRatingSerializer(ratings, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=('PATCH', 'PUT'))
    def update_availability(self, request, *args, **kwargs):
        merchant = self.get_object()
        serializer = AvailabilityMerchantSerializer(merchant, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        status_availability = serializer.save()
        return Response(self.set_response(status='ok', data={'status': status_availability},
                                          message='Cambio de disponibilidad correctamente'))

    @action(detail=True, methods=('PATCH',))
    def change_password(self, request, *args, **kwargs):
        customer = self.get_object()
        partial = request.method == 'PATCH'
        serializer = ChangePasswordMerchantSerializer(customer, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.set_response(status='ok', data={},
                                          message='Contraseña actualizada correctamente'))

    # Cache requested url for each user for 2 hours
    @action(detail=False, methods=['GET'])
    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_cookie)
    def home(self, request, *args, **kwargs):
        try:
            # Filtros
            category_id = self.request.query_params.get('category_id', 1)
            lat = self.request.query_params.get('lat', 18.462938)
            lng = self.request.query_params.get('lng', -97.392701)
            area_id = self.request.query_params.get('area_id', 1)
            category_model = CategoryMerchant.objects.get(id=category_id)
            sections = []
            filters_shared = {'area_id': area_id, 'information_is_complete': True, 'category_id': category_model.id,
                              'status_id': 1}
            # Cerca de ti
            nearest = self.get_nearest_merchants(area_id=area_id, category=category_model,
                                                 limit=settings.LIMIT_SECTIONS,
                                                 lat=lat, lng=lng,
                                                 filters=filters_shared)
            # Comprobar si hay comercios que mostrar
            if not nearest['has_data']:
                data = {
                    'more_merchants': False,
                    'secciones': [],
                    'tags': [],
                    'orders': 0,
                    'message': 'No hay comercios que mostrar'
                }
                return Response(data=data, status=status.HTTP_200_OK)
            # Mejores calificados
            section_2 = self.get_section_order_by(area_id=area_id, category=category_model,
                                                  section_name="Top de Los Pedidos",
                                                  section_description="Te presentamos los comercios con mejores calificaciones "
                                                                      "en nuestra plataforma.",
                                                  order_by="-reputation",
                                                  limit=settings.LIMIT_SECTIONS,
                                                  orientation="H",
                                                  filters=filters_shared,
                                                  picture='https://storage.googleapis.com/scooter_app/iconos_home/Recomendado.png')

            # Agregados recientemente
            section_3 = self.get_section_order_by(area_id, category=category_model,
                                                  section_name="Lo nuevo",
                                                  section_description="Comercios afiliados recientemente a Los "
                                                                      "Pedidos, conócelos…",
                                                  order_by="-created",
                                                  limit=settings.LIMIT_SECTIONS,
                                                  orientation="H",
                                                  filters=filters_shared,
                                                  picture='https://storage.googleapis.com/scooter_app/iconos_home/Recientemente.png')

            # Listado de comercios
            section_4 = self.get_section_order_by(area_id, category=category_model,
                                                  section_name=category_model.name,
                                                  section_description="",
                                                  order_by="created",
                                                  limit=40,
                                                  orientation="V",
                                                  filters=filters_shared,
                                                  picture=""
                                                  )

            sections.append(nearest)
            sections.append(section_2)
            sections.append(section_3)
            sections.append(section_4)
            tags = Tag.objects.filter(area_id=area_id, category_id=category_model.id)

            data = {
                'more_merchants': False,
                'secciones': sections,
                'tags': TagModelSimpleSerializer(tags, many=True).data,
                'orders': 0
            }

            return Response(data=data, status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex.__str__())
            data = self.set_error_response(status=False, field='detail',
                                           message='Ha ocurrido un error inesperado')
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_nearest_merchants(self, area_id, category, limit, lat, lng, filters):

        point = Point(x=float(lng), y=float(lat), srid=4326)
        merchants = Merchant.objects.filter(**filters) \
                        .annotate(distance=Distance('point', point)) \
                        .order_by('-is_open', 'distance')[0:limit]
        if len(merchants) == 0:
            return {
                'has_data': False
            }
        return {
            'has_data': True,
            'section_name': 'Cerca de ti',
            'section_description': "Estos son los comercios más cercanos según tu ubicación actual.",
            'orientation': 'H',
            'list': MerchantWithAllInfoSerializer(merchants, many=True).data,
            'more': False,
            'picture': 'https://storage.googleapis.com/scooter_app/iconos_home/Cerca%20de%20ti.png'
        }

    # Obtener seccion ordenado por un campo
    def get_section_order_by(self, area_id, category, section_name, section_description, order_by, limit, orientation,
                             filters, picture):
        merchants = Merchant.objects.filter(**filters) \
                        .order_by('-is_open', order_by, '-total_grades')[0:limit]

        if len(merchants) == 0:
            return {
                'has_data': False
            }
        if orientation == "V":
            merchants = self.iter_sample_fast(merchants, len(list(merchants)))
        return {
            'has_data': True,
            'section_name': section_name,
            'section_description': section_description,
            'orientation': orientation,
            'list': MerchantWithAllInfoSerializer(merchants, many=True).data,
            'more': False,
            'picture': picture
        }

    # Obtener secciones con filtros en los comercios
    def get_section_filters(self, area_id, section_name, filters):

        pass

    def get_section_random(self, area_id, section_name):

        pass

    def get_list_merchant_by_category(self, area_id, category_id, limit):

        pass

    def iter_sample_fast(self, iterable_list, samplesize):
        results = []
        iterator = iter(iterable_list)
        # Fill in the first samplesize elements:
        try:
            for _ in xrange(samplesize):
                results.append(iterator.__next__())
        except StopIteration:
            raise ValueError("Sample larger than population.")
        random.shuffle(results)  # Randomize their positions
        for i, v in enumerate(iterator, samplesize):
            r = random.randint(0, i)
            if r < samplesize:
                results[r] = v  # at a decreasing rate, replace random items
        return results
