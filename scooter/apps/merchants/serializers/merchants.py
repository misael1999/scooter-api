""" Merchants serializers """
# General
from datetime import timedelta
from django.utils import timezone
# Django
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import IntegrityError
# Django rest framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# Models
from scooter.apps.customers.serializers import PointSerializer
from scooter.apps.merchants.serializers.tags import MerchantTagSimpleSerializer
from scooter.apps.orders.models.ratings import RatingOrder
from scooter.apps.promotions.serializers import MerchantPromotionSimpleSerializer
from scooter.apps.users.models import User
from scooter.apps.merchants.models.merchants import Merchant, MerchantAddress, MerchantSchedule, TypeMenuMerchant, \
    MerchantDeliveryRule
from scooter.apps.common.models import Service, Schedule, CategoryMerchant, SubcategoryMerchant
# Utilities
from scooter.utils.functions import send_mail_verification, generate_verification_token
# Serializers
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
from scooter.apps.common.serializers import Base64ImageField


class MerchantDeliveryRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = MerchantDeliveryRule
        fields = '__all__'


class MerchantWithAllInfoSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    subcategory = serializers.StringRelatedField(read_only=True)
    # user = UserModelSimpleSerializer()
    delivery_rules = MerchantDeliveryRuleSerializer(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    promotions = serializers.SerializerMethodField('get_promotions', read_only=True)

    def get_promotions(self, merchant):
        qs = merchant.promotions.all()
        return MerchantPromotionSimpleSerializer(qs, many=True).data

    class Meta:
        model = Merchant
        geo_field = 'point'
        fields = ('id', 'email', 'contact_person', 'picture', 'merchant_name', 'phone_number', 'is_delivery_by_store',
                  'information_is_complete', 'category', 'total_grades', 'subcategory', 'reputation', 'description',
                  'approximate_preparation_time', 'full_address', 'is_open', 'point', 'from_preparation_time',
                  'to_preparation_time', 'type_menu', 'zone', 'area', 'delivery_rules', 'merchant_level',
                  'operational_zones_activated', 'restricted_zones_activated', 'accept_payment_online',
                  'has_rate_operating', 'increment_price_operating', 'tags', 'promotions')
        read_only_fields = fields


class MerchantUserSimpleSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    subcategory = serializers.StringRelatedField(read_only=True)
    user = UserModelSimpleSerializer()
    delivery_rules = MerchantDeliveryRuleSerializer(read_only=True)

    class Meta:
        model = Merchant
        geo_field = 'point'
        fields = ('id', 'email', 'user', 'contact_person', 'picture', 'merchant_name', 'phone_number', 'is_delivery_by_store',
                  'information_is_complete', 'category', 'subcategory', 'reputation', 'description',
                  'approximate_preparation_time', 'is_open', 'from_preparation_time', 'point',
                  'to_preparation_time', 'type_menu', 'area', 'zone', 'full_address', 'delivery_rules',
                  'merchant_level', 'operational_zones_activated', 'restricted_zones_activated', 'accept_payment_online',
                  'has_rate_operating', 'increment_price_operating'
)
        read_only_fields = fields


class AvailabilityMerchantSerializer(serializers.Serializer):
    is_open = serializers.BooleanField()

    def update(self, merchant, data):
        merchant.is_open = data['is_open']
        merchant.save()
        return merchant.is_open


class ChangePasswordMerchantSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=60)
    new_password = serializers.CharField(min_length=8, max_length=60)

    def update(self, instance, data):
        try:
            # Check if current_password is correct
            if not instance.user.check_password(data['current_password']):
                raise ValueError('La contraseña actual no es correcta')

            instance.user.set_password(data['new_password'])
            instance.user.save()
            return instance
        except ValueError as ex:
            raise serializers.ValidationError({'detail': str(ex)})
        except Exception as e:
            raise serializers.ValidationError({'detail': 'Ha ocurrido un error desconocido'})


# ===============
# Serializers to update info of merchant
# ===============


class GeneralInfoMerchantSerializer(serializers.Serializer):
    picture = Base64ImageField()
    merchant_name = serializers.CharField(max_length=80)
    contact_person = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(max_length=120, required=False, allow_null=True, allow_blank=True)
    approximate_preparation_time = serializers.CharField(max_length=10)
    from_preparation_time = serializers.FloatField()
    to_preparation_time = serializers.FloatField()
    operational_zones_activated = serializers.BooleanField(required=False)
    restricted_zones_activated = serializers.BooleanField(required=False)
    has_rate_operating = serializers.BooleanField(required=False)
    increment_price_operating = serializers.FloatField(required=False)


# Merchant Schedule
class MerchantScheduleSerializer(serializers.ModelSerializer):
    schedule_id = serializers.PrimaryKeyRelatedField(queryset=Schedule.objects.all(), source="schedule")
    schedule = serializers.StringRelatedField(read_only=True, required=False)

    class Meta:
        model = MerchantSchedule
        fields = ("schedule_id", "from_hour", "to_hour", "schedule", 'is_open')


class MerchantAddressSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(max_length=300)
    point = PointSerializer(required=False)

    class Meta:
        model = MerchantAddress
        fields = ('full_address', 'references', 'point')


class MerchantInfoSerializer(serializers.ModelSerializer):
    schedules = MerchantScheduleSerializer(many=True)
    user = UserModelSimpleSerializer()
    delivery_rules = MerchantDeliveryRuleSerializer(read_only=True)
    tags = MerchantTagSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Merchant
        geo_field = 'point'
        fields = ('id', 'email', 'user', 'contact_person', 'picture', 'merchant_name', 'phone_number',
                  'information_is_complete', 'is_delivery_by_store', 'reputation', 'description', 'total_grades',
                  'approximate_preparation_time', 'is_open', 'point', 'from_preparation_time',
                  'to_preparation_time', 'schedules', 'full_address', 'zone', 'area', 'delivery_rules',
                  'merchant_level', 'operational_zones_activated', 'restricted_zones_activated',
                  'accept_payment_online','has_rate_operating', 'increment_price_operating', "tags")
        read_only_fields = fields


class MerchantRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingOrder
        fields = ('id',
                  'order',
                  'delivery_man',
                  'rating_customer',
                  'comments',
                  'rating',
                  'rating_merchant'
                  )
        depth = 1
        read_only_fields = fields


# Update info of merchant
class UpdateInfoMerchantSerializer(serializers.Serializer):
    schedules = MerchantScheduleSerializer(many=True)
    address = MerchantAddressSerializer()
    general = GeneralInfoMerchantSerializer()

    def update(self, instance, data):
        """ Update merchant info """
        try:
            # Variables
            schedules_to_save = []
            schedules_to_update = []
            address_to_save = None

            # Save general info
            general = data.pop('general', None)
            if general:
                instance = self.save_general_info(instance=instance, general=general)

            # Save config
            schedules = data.pop('schedules', None)

            if schedules:
                schedules_dict = self.save_schedules(instance, schedules)
                schedules_to_save = schedules_dict['save']
                schedules_to_update = schedules_dict['update']

            # Save merchant address
            address = data.pop('address', None)
            if address:
                address_to_save = self.save_merchant_address(instance=instance, address=address)

            # Save all models
            self.save_all_models(instance=instance, schedules_to_save=schedules_to_save,
                                 schedules_to_update=schedules_to_update,
                                 address_to_save=address_to_save)

            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': e})
        except Exception as ex:
            print("Exception save info merchant main method, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al actualizar la información'})

    def save_general_info(self, instance, general):
        """ Before updating we have to delete the previous image """
        try:
            # import pdb; pdb.set_trace()
            if general.get('picture', None) is not None:
                instance.picture.delete()
            for field, value in general.items():
                setattr(instance, field, value)
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception save general info, please check it")
            print(ex.args.__str__())
            raise ValueError(str(ex))

    def save_schedules(self, instance, schedules):
        """ Save array of merchant schedules """
        try:
            schedules_to_save = []
            schedules_to_update = []
            for schedule in schedules:
                """ add each schedule in an array and then save it with the function bulk_create """
                merchant_schedule = MerchantSchedule.objects.filter(merchant=instance, schedule=schedule['schedule'])
                if merchant_schedule:
                    sta_schedule = merchant_schedule[0]
                    for field, value in schedule.items():
                        setattr(sta_schedule, field, value)
                    schedules_to_update.append(sta_schedule)
                    continue

                schedules_to_save.append(MerchantSchedule(**schedule, merchant=instance))

            return {'save': schedules_to_save, 'update': schedules_to_update}
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as ex:
            print("Exception save schedules, please check it")
            print(ex.args.__str__())
            raise ValueError(str(ex))

    def save_merchant_address(self, instance, address):
        try:
            data_point = address.pop('point', None)
            point = Point(x=data_point['lng'], y=data_point['lat'])
            address['point'] = point
            return address
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as ex:
            print("Exception save merchant address, please check it")
            print(ex.args.__str__())
            raise ValueError(str(ex))

    def save_all_models(self, instance, schedules_to_save, schedules_to_update, address_to_save):

        """ Save all data if everything goes well """
        try:
            MerchantSchedule.objects.bulk_create(schedules_to_save)
            MerchantSchedule.objects.bulk_update(schedules_to_update, fields=["is_open", "from_hour", "to_hour"])

            if address_to_save:
                address_exist = MerchantAddress.objects.filter(merchant=instance)
                # If exist address update attribute and if it not exist create
                if address_exist.exists():
                    merchant_address = address_exist[0]
                    for field, value in address_to_save.items():
                        setattr(merchant_address, field, value)
                    merchant_address.save()
                else:
                    MerchantAddress(**address_to_save, merchant=instance).save()
                instance.point = address_to_save['point']
                instance.full_address = address_to_save['full_address']

            instance.information_is_complete = True
            instance.save()

            return instance
        except IntegrityError as iex:
            print(str(iex))
            raise ValueError(str('Revisar si ingreso llaves primarias repetidas'))
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as ex:
            print("Exception save all models, please check it")
            print(ex.args.__str__())
            raise ValueError(str(ex))


# Create a new merchant
class MerchantSignUpSerializer(serializers.Serializer):
    """ Serializer only to register a new merchant """
    username = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='El email ya esta en uso')])

    contact_person = serializers.CharField(max_length=60)
    password = serializers.CharField(min_length=8, max_length=64)
    phone_number = serializers.CharField(max_length=15)
    category_id = serializers.PrimaryKeyRelatedField(queryset=CategoryMerchant.objects.all(), source="category")
    subcategory_id = serializers.PrimaryKeyRelatedField(queryset=SubcategoryMerchant.objects.all(),
                                                        source="subcategory",
                                                        required=False, allow_null=True)
    is_delivery_by_store = serializers.BooleanField(default=False)
    type_menu = serializers.PrimaryKeyRelatedField(queryset=TypeMenuMerchant.objects.all())
    merchant_name = serializers.CharField(max_length=100, validators=[UniqueValidator(
        queryset=Merchant.objects.all(),
        message='Ya existe un negocio con el mismo nombre. ¿El negocio es tuyo?,'
                ' comunicate con nosotros scooterenvios@gmail.com')])

    def create(self, data):
        try:
            username = data.pop('username')
            user = User(username=username,
                        is_verified=True,
                        role=User.MERCHANT,
                        is_client=False,
                        verification_deadline=timezone.localtime(timezone.now()) + timedelta(days=2))

            password = data.pop('password')
            user.set_password(password)
            user.save()
            merchant = Merchant.objects.create(**data,
                                               email=username,
                                               user=user)

            # code = generate_verification_token(user=user,
            #                                    exp=timezone.localtime(timezone.now()) + timedelta(minutes=20),
            #                                    token_type='email_confirmation')

            subject = 'Bienvenido {name}'.format(name=merchant.merchant_name)
            data = {
                'email': username,
                'name': merchant.merchant_name,
                'password': password,
                'url': settings.URL_SERVER_FRONTEND
            }
            # send_email = send_mail_verification(subject=subject,
            #                                     to_user=user.username,
            #                                     path_template="emails/merchants/welcome.html",
            #                                     data=data)
            # if not send_email:
            #     raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar el correo'})

            return user
        except Exception as ex:
            return serializers.ValidationError({'detail': 'Ha ocurrido un problema al registrarse'})
