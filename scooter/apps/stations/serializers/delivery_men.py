""" Station delivery man serializers """
# General
from django.utils import timezone
# Django rest framework
from rest_framework import serializers
from django.contrib.gis.geos import Point
# Models
from scooter.apps.common.models import Service, Status
from scooter.apps.orders.models import Order
from scooter.apps.stations.models import Vehicle
from scooter.apps.stations.serializers.vehicles import VehicleModelSerializer
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


class DeliveryManAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryManAddress
        fields = (
            'street', 'suburb', 'postal_code',
            'exterior_number', 'inside_number', 'references'
        )


class DeliveryManModelSerializer(ScooterModelSerializer):
    delivery_status = serializers.StringRelatedField(read_only=True)
    status = serializers.StringRelatedField()
    picture = Base64ImageField(use_url=True)
    vehicle = VehicleModelSerializer()
    address = DeliveryManAddressSerializer()

    class Meta:
        model = DeliveryMan
        geo_field = 'location'
        fields = (
            'id', 'user', 'station','status', 'vehicle',
            'name', 'last_name', 'phone_number',
            'picture', 'salary_per_order', 'total_orders', 'reputation',
            'location', 'delivery_status', 'address')
        read_only_fields = fields


class DeliveryManUserModelSerializer(ScooterModelSerializer):
    user = UserModelSimpleSerializer()

    class Meta:
        model = DeliveryMan
        fields = '__all__'
        read_only_fields = (
            'reputation',
        )


class DeliveryManWithAddressSerializer(serializers.ModelSerializer):
    address = DeliveryManAddressSerializer()
    picture = Base64ImageField(use_url=True)
    vehicle = VehicleModelSerializer()
    status = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DeliveryMan
        geo_field = 'location'
        fields = (
            'id', 'user', 'station', 'vehicle',
            'name', 'last_name', 'phone_number', 'status',
            'picture', 'salary_per_order', 'total_orders', 'reputation',
            'location', 'delivery_status', 'address')
        read_only_fields = fields


class CreateDeliveryManSerializer(serializers.ModelSerializer):
    picture = Base64ImageField(required=False, use_url=True)
    password = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=60)
    last_name = serializers.CharField(max_length=60)
    phone_number = serializers.CharField(max_length=15)
    salary_per_order = serializers.FloatField(default=0)
    address = DeliveryManAddressSerializer()
    vehicle_id = StationFilteredPrimaryKeyRelatedField(queryset=Vehicle.objects, source="vehicle")
    status_id = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), source="status", required=False)

    class Meta:
        model = DeliveryMan
        fields = (
            'picture', 'password', 'name',
            'last_name', 'phone_number', 'salary_per_order', 'address', 'vehicle_id', 'status_id'
        )

    def validate(self, data):
        phone_number = data.get('phone_number', None)
        delivery_instance = self.context['delivery_instance']
        user_exist = User.objects.filter(username=phone_number).exists()
        if user_exist and not delivery_instance:
            raise serializers.ValidationError({'detail': 'Ya se encuentra un repartidor con ese numero de telefono'},
                                              code='delivery_exist')
        if user_exist and delivery_instance.user.username != phone_number:
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
                        role=User.DELIVERY_MAN,
                        verification_deadline=timezone.now())

            user.set_password(data['password'])
            user.save()

            # Verify that the vehicle is no assign the other delivery man and remove if exist one
            delivery_man_vehicle = DeliveryMan.objects.filter(vehicle=data['vehicle']).first()

            if delivery_man_vehicle:
                delivery_man_vehicle.vehicle = None
                delivery_man_vehicle.save()

            delivery_man = DeliveryMan.objects.create(name=data['name'],
                                                      last_name=data['last_name'],
                                                      phone_number=data['phone_number'],
                                                      user=user,
                                                      vehicle=data['vehicle'],
                                                      station=station)
            DeliveryManAddress.objects.create(**address, delivery_man=delivery_man)

            # in the future send an email to the station when a new delivery man register
            return delivery_man
        except Exception as ex:
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Ha ocurrido un problema al registrarse un repartidor'})

    def update(self, instance, data):
        try:
            address = data.pop('address', None)
            vehicle = data.get('vehicle', None)

            if vehicle:
                delivery_man_vehicle = DeliveryMan.objects.filter(vehicle=vehicle).first()

                if delivery_man_vehicle:
                    delivery_man_vehicle.vehicle = None
                    delivery_man_vehicle.save()

            phone_number = data.get('phone_number', None)
            super().update(instance, data)

            if address:
                # DeliveryManAddress.objects.create(**address, delivery_man=instance)
                DeliveryManAddress.objects.filter(pk=instance.address.id).update(**address)

            if phone_number:
                instance.user.username = phone_number
                instance.user.save()

            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in update delivery man, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al actualizar el repartidor'})


class GetDeliveryMenNearestSerializer(serializers.Serializer):
    order_id = StationFilteredPrimaryKeyRelatedField(queryset=Order.objects, source="order")
    distance = serializers.IntegerField(default=5)
    type_service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="type_service")

    def create(self, data):
        try:
            station = self.context['station']
            request = self.context['request']
            type_service = data['type_service']
            order = data['order']

            filters = dict()
            is_all = request.query_params.get('all', None)
            # Is a filter to show all or only are the available
            if is_all == 'false':
                filters['delivery_status'] = 1

            location_selected = None
            if type_service.slug_name == 'pick_up':
                location_selected = order.from_address
            else:
                location_selected = order.to_address

            # List of delivery men nearest (from_location)
            delivery_men = DeliveryMan.objects.filter(**filters, status__slug_name="active",
                                                      station=station
                                                      ).annotate(
                distance=Distance("location", location_selected.point)).order_by("distance")
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

