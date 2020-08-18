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
from scooter.apps.users.models import User
from scooter.apps.merchants.models.merchants import Merchant, MerchantAddress, MerchantSchedule
from scooter.apps.common.models import Service, Schedule, CategoryMerchant, SubcategoryMerchant
# Utilities
from scooter.utils.functions import send_mail_verification, generate_verification_token
# Serializers
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
from scooter.apps.common.serializers import Base64ImageField


class MerchantWithAllInfoSerializer(serializers.ModelSerializer):

    category = serializers.StringRelatedField(read_only=True)
    subcategory = serializers.StringRelatedField(read_only=True)
    user = UserModelSimpleSerializer()

    class Meta:
        model = Merchant
        fields = ('id', 'user', 'contact_person', 'picture', 'merchant_name', 'phone_number', 'is_delivery_by_store',
                  'information_is_complete', 'category', 'subcategory', 'reputation', 'description', 'approximate_preparation_time')
        read_only_fields = fields


class MerchantUserSimpleSerializer(serializers.ModelSerializer):

    category = serializers.StringRelatedField(read_only=True)
    subcategory = serializers.StringRelatedField(read_only=True)
    user = UserModelSimpleSerializer()

    class Meta:
        model = Merchant
        fields = ('id', 'user', 'contact_person', 'picture', 'merchant_name', 'phone_number', 'is_delivery_by_store',
                  'information_is_complete', 'category', 'subcategory', 'reputation')
        read_only_fields = fields

# ===============
# Serializers to update info of merchant
# ===============


class GeneralInfoMerchantSerializer(serializers.Serializer):
    picture = Base64ImageField()
    merchant_name = serializers.CharField(max_length=80)
    description = serializers.CharField(max_length=120, required=False, allow_null=True, allow_blank=True)
    approximate_preparation_time = serializers.CharField(max_length=10)


# Merchant Schedule
class MerchantScheduleSerializer(serializers.ModelSerializer):
    schedule_id = serializers.PrimaryKeyRelatedField(queryset=Schedule.objects.all(), source="schedule")
    schedule = serializers.StringRelatedField(read_only=True, required=False)

    class Meta:
        model = MerchantSchedule
        fields = ("schedule_id", "from_hour", "to_hour", "schedule")


class MerchantAddressSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(max_length=300)
    point = PointSerializer(required=False)

    class Meta:
        model = MerchantAddress
        fields = ('full_address', 'references', 'point')


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
            instance.information_is_complete = True
            instance.save()
            MerchantSchedule.objects.bulk_create(schedules_to_save)
            MerchantSchedule.objects.bulk_update(schedules_to_update, fields=["from_hour", "to_hour"])

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
    merchant_name = serializers.CharField(max_length=100, validators=[UniqueValidator(
        queryset=Merchant.objects.all(),
        message='Ya existe un negocio con el mismo nombre. ¿El negocio es tuyo?,'
                ' comunicate con nosotros scooterenvios@gmail.com')])

    def create(self, data):
        try:
            user = User(username=data.pop('username'),
                        is_verified=True,
                        role=User.MERCHANT,
                        is_client=False,
                        verification_deadline=timezone.localtime(timezone.now()) + timedelta(days=2))

            password = data.pop('password')
            user.set_password(password)
            user.save()
            merchant = Merchant.objects.create(**data,
                                               user=user)

            # code = generate_verification_token(user=user,
            #                                    exp=timezone.localtime(timezone.now()) + timedelta(minutes=20),
            #                                    token_type='email_confirmation')

            subject = 'Bienvenido {name}'.format(name=merchant.merchant_name)
            data = {
                'email': user.username,
                'name': merchant.merchant_name,
                'password': password,
                'url': settings.URL_SERVER_FRONTEND
            }
            send_email = send_mail_verification(subject=subject,
                                                to_user=user.username,
                                                path_template="emails/merchants/welcome.html",
                                                data=data)
            if not send_email:
                raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar el correo'})
            return user

        except Exception as ex:
            return serializers.ValidationError({'detail': 'Ha ocurrido un problema al registrarse'})
