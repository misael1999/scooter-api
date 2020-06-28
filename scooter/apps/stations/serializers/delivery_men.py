""" Station delivery man serializers """
# General
from django.utils import timezone
# Django rest framework
from rest_framework import serializers
from django.contrib.gis.geos import Point
# Models
from scooter.apps.orders.models import Order
from scooter.apps.users.models import User
from scooter.apps.delivery_men.models.delivery_men import DeliveryMan, DeliveryManAddress
from scooter.apps.customers.models import CustomerAddress
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer
from scooter.apps.common.serializers.common import StationFilteredPrimaryKeyRelatedField
# Serializers
from scooter.apps.common.serializers import Base64ImageField
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
# Django Geo
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance


class DeliveryManModelSerializer(ScooterModelSerializer):
    delivery_status = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DeliveryMan
        geo_field = 'location'
        fields = (
            'id', 'user', 'station',
            'name', 'last_name', 'phone_number',
            'picture', 'salary_per_order', 'total_orders', 'reputation',
            'location', 'delivery_status')
        read_only_fields = fields


class DeliveryManUserModelSerializer(ScooterModelSerializer):
    user = UserModelSimpleSerializer()

    class Meta:
        model = DeliveryMan
        fields = '__all__'
        read_only_fields = (
            'reputation',
        )


class DeliveryManAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryManAddress
        fields = (
            'street', 'suburb', 'postal_code',
            'exterior_number', 'inside_number', 'references'
        )


class DeliveryManWithAddressSerializer(serializers.ModelSerializer):
    address = DeliveryManAddressSerializer()

    class Meta:
        model = DeliveryMan
        geo_field = 'location'
        fields = (
            'id', 'user', 'station',
            'name', 'last_name', 'phone_number',
            'picture', 'salary_per_order', 'total_orders', 'reputation',
            'location', 'delivery_status', 'address')
        read_only_fields = fields


class CreateDeliveryManSerializer(serializers.Serializer):
    picture = Base64ImageField(required=False)
    password = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=60)
    last_name = serializers.CharField(max_length=60)
    phone_number = serializers.CharField(max_length=15)
    salary_per_order = serializers.FloatField(default=0)
    address = DeliveryManAddressSerializer()

    def validate(self, data):
        user_exist = User.objects.filter(username=data['phone_number']).exists()
        if user_exist:
            raise serializers.ValidationError({'detail': 'Ya se encuentra un repartidor con ese numero de telefono'},
                                              code='delivery_exist')
        return data

    def create(self, data):
        try:
            station = self.context['station']
            address = data.pop('address', None)
            user = User(username=data['phone_number'],
                        is_client=False,
                        is_verified=True,
                        verification_deadline=timezone.now())

            user.set_password(data['password'])
            user.save()

            delivery_man = DeliveryMan.objects.create(name=data['name'],
                                                      last_name=data['last_name'],
                                                      phone_number=data['phone_number'],
                                                      user=user,
                                                      station=station)
            DeliveryManAddress.objects.create(**address, delivery_man=delivery_man)

            # in the future send an email to the station when a new delivery man register
            return delivery_man
        except Exception as ex:
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Ha ocurrido un problema al registrarse un repartidor'})


class GetDeliveryMenNearestSerializer(serializers.Serializer):
    order_id = StationFilteredPrimaryKeyRelatedField(queryset=Order.objects, source="order")
    distance = serializers.IntegerField(default=5)

    def create(self, data):
        try:
            station = self.context['station']
            order = data['order']
            request = self.context['request']
            is_all = request.query_params.get('all', None)
            filters = dict()
            if is_all == 'false':
                filters['delivery_status'] = 1
            from_location = order.from_address
            # List of delivery men nearest (from_location)
            delivery_men = DeliveryMan.objects.filter(**filters, station=station,
                                                      location__distance_lte=(
                                                          from_location.point, D(km=data['distance']))
                                                      ).annotate(
                distance=Distance("location", from_location.point)).order_by("distance")
            # delivery_men = DeliveryMan.objects.filter(station=station).annotate(
            #     distance=Distance('location', from_location.point)
            # ).order_by('distance')

            if not delivery_men:
                raise ValueError('No se encontraron repartidores')

            return delivery_men
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in get delivery man nearest, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al consultar los repartidores'})
