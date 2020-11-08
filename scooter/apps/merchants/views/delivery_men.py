""" Merchant Delivery men view """
# Django rest
from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Models
from scooter.apps.common.models import Status
from scooter.apps.delivery_men.models.delivery_men import DeliveryMan
from scooter.apps.orders.models import Order
# Serializers
from scooter.apps.orders.serializers import OrderWithDetailSimpleSerializer
from scooter.apps.merchants.serializers.delivery_men import (CreateDeliveryManSerializer,
                                                             DeliveryManModelSerializer,
                                                             DeliveryManWithAddressSerializer)
# Viewset
from scooter.apps.merchants.utils import MerchantDeliveryManFilter
from scooter.utils.viewsets.scooter import ScooterViewSet
# Mixins
from scooter.apps.common.mixins.merchants import AddMerchantMixin
# Permissions
from rest_framework.permissions import IsAuthenticated
from scooter.apps.merchants.permissions import IsAccountOwnerMerchant
# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
# Functions
from scooter.utils.functions import get_date_from_querystring
from datetime import timedelta


class DeliveryMenMerchantViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                                 mixins.DestroyModelMixin,
                                 mixins.UpdateModelMixin, mixins.CreateModelMixin,
                                 mixins.ListModelMixin, AddMerchantMixin):
    """ View set for the merchants can register a new delivery man """

    serializer_class = DeliveryManModelSerializer
    queryset = DeliveryMan.objects.all()
    permission_classes = (IsAuthenticated, IsAccountOwnerMerchant)
    merchant = None
    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name', 'phone_number')
    ordering_fields = ('name', 'reputation')
    # Affect the default order
    # ordering = ('-created', 'passengers__count')
    filter_class = MerchantDeliveryManFilter

    """ Method dispatch in AddMerchantMixin """

    def get_queryset(self):
        """ Personalized query when the action is a list so that it only returns active delivery men """
        if self.action in ['list', 'nearest', 'retrieve']:
            return self.merchant.deliveryman_set.all()

        return self.queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action in ['create', 'partial_update', 'update']:
            serializer_class = CreateDeliveryManSerializer
        if self.action == 'retrieve':
            return DeliveryManWithAddressSerializer
        return serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = self.set_response(status=True,
                                 data=DeliveryManModelSerializer(obj).data,
                                 message='Se ha registrado un nuevo repartidor')
        return Response(data=data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        from_date = get_date_from_querystring(self.request, 'from_date', timezone.localtime(timezone.now()))
        to_date = get_date_from_querystring(self.request, 'to_date',
                                            timezone.localtime(timezone.now()) + timedelta(days=1))

        # History order from date
        history_orders = Order.objects.filter(date_delivered_order__range=(from_date, to_date),
                                              delivery_man=response.data['id'])
        response.data['history_orders'] = OrderWithDetailSimpleSerializer(history_orders, many=True).data
        response.data['total_orders_date'] = history_orders.count()

        return response

    def update(self, request, *args, **kwargs):
        delivery_man = self.get_object()
        serializer = self.get_serializer(delivery_man, data=request.data, partial=True,
                                         context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        delivery = serializer.save()
        # delivery_man_created = CreateDeliveryManSerializer(delivery_man).data
        data = self.set_response(status=True, data={}, message="Repartidor actualizado correctamente")
        return Response(data=data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """Disable delivery man."""
        general_status = Status.objects.get(slug_name="inactive")
        instance.delivery_status.id = 3
        instance.status = general_status
        instance.save()

    @action(detail=True, methods=['PUT'])
    def unlock(self, request, *args, **kwargs):
        delivery_man = self.get_object()
        sts = Status.objects.get(slug_name='active')
        # Send instance of vehicle for validate of name not exist
        delivery_man.status = sts
        delivery_man.save()
        data = self.set_response(status=True, data={}, message="Repartidor desbloqueado correctamente")
        return Response(data=data, status=status.HTTP_200_OK)