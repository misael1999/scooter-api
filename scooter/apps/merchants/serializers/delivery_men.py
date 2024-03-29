""" Merchant delivery man serializers """
# General
from django.utils import timezone
# Django rest framework
from rest_framework import serializers
# Models
from rest_framework.validators import UniqueValidator

from scooter.apps.common.models import Service
from scooter.apps.orders.models import Order
from scooter.apps.users.models import User
from scooter.apps.delivery_men.models.delivery_men import DeliveryMan, DeliveryManAddress
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer
from scooter.apps.common.serializers.common import StationFilteredPrimaryKeyRelatedField
# Serializers
from scooter.apps.common.serializers import Base64ImageField
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
# Django Geo
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
    vehicle_type = serializers.StringRelatedField(read_only=True)
    status = serializers.StringRelatedField()
    picture = Base64ImageField(use_url=True)
    address = DeliveryManAddressSerializer()

    class Meta:
        model = DeliveryMan
        geo_field = 'location'
        fields = (
            'id', 'user', 'station', 'merchant', 'status',
            'name', 'last_name', 'phone_number', 'picture', 'reputation',
            'location', 'delivery_status', 'address', 'vehicle_plate', 'vehicle_model',
            'vehicle_year', 'vehicle_color', 'vehicle_type', 'vehicle_type_id')
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
    status = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DeliveryMan
        geo_field = 'location'
        fields = (
            'id', 'user', 'station', 'merchant', 'vehicle',
            'name', 'last_name', 'phone_number', 'status',
            'picture', 'reputation', 'last_time_update_location', 'from_merchant',
            'location', 'delivery_status', 'address')
        read_only_fields = fields


class CreateDeliveryManSerializer(serializers.ModelSerializer):
    picture = Base64ImageField(required=False, use_url=True)
    password = serializers.CharField(max_length=50)
    address = DeliveryManAddressSerializer(required=False)
    phone_number = serializers.CharField(max_length=70,
                                         validators=
                                         [UniqueValidator(
                                             queryset=DeliveryMan.objects.all(),
                                             message='Ya existe un repartidor con ese numero de telefono')])

    class Meta:
        model = DeliveryMan
        fields = (
            'picture', 'password', 'name', 'last_name',
            'phone_number', 'address', 'vehicle_plate', 'vehicle_model',
            'vehicle_year', 'vehicle_color', 'vehicle_type'
        )

    # def validate(self, data):
    #     phone_number = data.get('phone_number', None)
    #     delivery_instance = self.context['delivery_instance']
    #     user_exist = User.objects.filter(username=phone_number).exists()
    #     if user_exist and not delivery_instance:
    #         raise serializers.ValidationError({'detail': 'Ya se encuentra un repartidor con ese numero de telefono'},
    #                                           code='delivery_exist')
    #     if user_exist and delivery_instance.user.username != phone_number:
    #         raise serializers.ValidationError({'detail': 'Ya se encuentra un repartidor con ese numero de telefono'},
    #                                           code='delivery_exist')
    #     return data

    def create(self, data):
        try:
            merchant = self.context['merchant']
            address = data.pop('address', None)
            password = data.pop('password', None)
            user = User(username=data['phone_number'],
                        is_client=False,
                        is_verified=True,
                        role=User.DELIVERY_MAN,
                        verification_deadline=timezone.now())

            user.set_password(password)
            user.save()

            delivery_man = DeliveryMan.objects.create(**data,
                                                      from_merchant=True,
                                                      user=user,
                                                      delivery_status_id=3,
                                                      merchant=merchant)
            if address:
                DeliveryManAddress.objects.create(**address, delivery_man=delivery_man)

            return delivery_man
        except Exception as ex:
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Ha ocurrido un problema al registrar un repartidor'})

    def update(self, instance, data):
        try:
            address = data.pop('address', None)
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
            print("Exception in update delivery man from merchant, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al actualizar el repartidor'})

# class GetDeliveryMenNearestSerializer(serializers.Serializer):
#     order_id = StationFilteredPrimaryKeyRelatedField(queryset=Order.objects, source="order")
#     distance = serializers.IntegerField(default=5)
#     type_service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="type_service")
#
#     def create(self, data):
#         try:
#             station = self.context['station']
#             request = self.context['request']
#             type_service = data['type_service']
#             order = data['order']
#
#             filters = dict()
#             is_all = request.query_params.get('all', None)
#             # Is a filter to show all or only are the available
#             if is_all == 'false':
#                 filters['delivery_status'] = 1
#
#             location_selected = None
#             if type_service.slug_name == 'pick_up':
#                 location_selected = order.from_address
#             else:
#                 location_selected = order.to_address
#
#             # List of delivery men nearest (from_location)
#             delivery_men = DeliveryMan.objects.filter(**filters, status__slug_name="active",
#                                                       station=station
#                                                       ).annotate(
#                 distance=Distance("location", location_selected.point)).order_by("distance")
#             # delivery_men = DeliveryMan.objects.filter(station=station).annotate(
#             #     distance=Distance('location', from_location.point)
#             # ).order_by('distance')
#
#             if not delivery_men:
#                 raise ValueError('No se encontraron repartidores')
#
#             return delivery_men
#         except ValueError as e:
#             raise serializers.ValidationError({'detail': str(e)})
#         except Exception as ex:
#             print("Exception in get delivery man nearest, please check it")
#             print(ex.args.__str__())
#             raise serializers.ValidationError({'detail': 'Error al consultar los repartidores'})
