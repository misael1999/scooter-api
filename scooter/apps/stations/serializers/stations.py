""" Users serializers """
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
from scooter.apps.users.models import User
from scooter.apps.stations.models.stations import Station, StationAddress, StationSchedule, StationService
from scooter.apps.common.models import Service, Schedule
# Utilities
from scooter.utils.functions import send_mail_verification, generate_verification_token
# Serializers
from scooter.apps.users.serializers.users import UserModelSimpleSerializer
from scooter.apps.common.serializers import Base64ImageField


class StationSimpleModelSerializer(serializers.ModelSerializer):
    picture = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = Station
        fields = '__all__'
        read_only_fields = (
            'reputation',
            'total_orders',
            'total_clients',
            'total_delivery_man',
            'total_messages_support',
            'station_verified',
            'user',
            'station_name',
        )

    def update(self, instance, validated_data):
        """ Before updating we have to delete the previous image """
        try:
            instance.picture.delete(save=True)
        except Exception as ex:
            print("Exception deleting image client, please check it")
            print(ex.args.__str__())
        return super().update(instance, validated_data)


class StationUserModelSerializer(serializers.ModelSerializer):
    user = UserModelSimpleSerializer()

    class Meta:
        model = Station
        exclude = ('created', 'modified')
        read_only_fields = (
            'reputation',
            'total_orders',
            'total_clients',
            'total_delivery_man',
            'total_messages_support',
            'station_verified',
            'user',
            'station_name',
        )


# Serializers of helps =================
class PointSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


# General information
class GeneralInfoSerializer(serializers.Serializer):
    picture = Base64ImageField(required=False)


# Rates by service
class RatesServicesSerializer(serializers.Serializer):
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source="service")
    base_rate_price = serializers.FloatField()
    price_kilometer = serializers.FloatField()
    from_kilometer = serializers.FloatField()
    to_kilometer = serializers.FloatField()

    def validate(self, data):
        if data['from_kilometer'] > 0:
            raise serializers.ValidationError('La tarifa base debe de empezar desde el km 0')
        return data


# Station address
class StationAddressSerializer(serializers.ModelSerializer):
    point = PointSerializer(required=False)

    class Meta:
        model = StationAddress
        fields = ("street", "suburb", "postal_code",
                  "exterior_number", "inside_number", "references",
                  "point")


# Station Schedule
class StationScheduleSerializer(serializers.ModelSerializer):
    schedule_id = serializers.PrimaryKeyRelatedField(queryset=Schedule.objects.all(), source="schedule")

    class Meta:
        model = StationSchedule
        fields = ("schedule_id", "from_hour", "to_hour")

    def validate(self, data):

        if data['from_hour'] > data['to_hour']:
            raise serializers.ValidationError('La hora de apertura debe ser mayor')

        return data


# Other configurations
class StationConfigSerializer(serializers.Serializer):
    assign_delivery_manually = serializers.BooleanField()
    cancellation_policies = serializers.CharField(max_length=400)
    allow_cancellations = serializers.BooleanField()
    schedules = StationScheduleSerializer(many=True)


# Update configuration of station
class StationUpdateInfoSerializer(serializers.Serializer):
    general = GeneralInfoSerializer(required=False)
    config = StationConfigSerializer()
    services = RatesServicesSerializer(many=True)
    address = StationAddressSerializer()

    def update(self, instance, data):
        """ Update station info"""
        try:

            # Variables
            schedules_to_save = []
            schedules_to_update = []
            address_to_save = None
            services_to_update = []
            services_to_save = []

            # Save general info
            general = data.pop('general', None)
            if general:
                instance = self.save_general_info(instance=instance, general=general)

            # Save config
            config = data.pop('config', None)
            if config:
                instance = self.save_config(instance=instance, config=config)

            schedules = config.pop('schedules', None)
            if schedules:
                schedules_dict = self.save_schedules(instance, schedules)
                schedules_to_save = schedules_dict['save']
                schedules_to_update = schedules_dict['update']

            # Save station address
            address = data.pop('address', None)
            if address:
                address_to_save = self.save_station_address(instance=instance, address=address)

            # Save station services
            services = data.pop('services', None)
            if services:
                services_dict = self.save_station_services(instance=instance, services=services)
                services_to_save = services_dict['save']
                services_to_update = services_dict['update']

            # Save all models
            self.save_all_models(instance=instance, schedules_to_save=schedules_to_save,
                                 schedules_to_update=schedules_to_update,
                                 address_to_save=address_to_save, services_to_update=services_to_update,
                                 services_to_save=services_to_save)

            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': e})
        except Exception as ex:
            print("Exception save info station main method, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al actualizar la información'})

    def save_general_info(self, instance, general):
        """ Before updating we have to delete the previous image """
        try:
            # import pdb; pdb.set_trace()
            instance.picture.delete()
            instance.picture = general['picture']
            return instance
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception save general info, please check it")
            print(ex.args.__str__())
            raise ValueError(str(ex))

    def save_config(self, instance, config):
        """ Save station config """
        try:
            instance.assign_delivery_manually = config['assign_delivery_manually']
            instance.cancellation_policies = config['cancellation_policies']
            instance.allow_cancellations = config['allow_cancellations']
            return instance
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as ex:
            print("Exception save station config, please check it")
            print(ex.args.__str__())
            raise ValueError(str(ex))

    def save_schedules(self, instance, schedules):
        """ Save array of station schedules """
        try:
            schedules_to_save = []
            schedules_to_update = []
            for schedule in schedules:
                """ add each schedule in an array and then save it with the function bulk_create """
                station_schedule = StationSchedule.objects.filter(station=instance, schedule=schedule['schedule'])
                if station_schedule:
                    sta_schedule = station_schedule[0]
                    for field, value in schedule.items():
                        setattr(sta_schedule, field, value)

                    schedules_to_update.append(sta_schedule)
                    continue

                schedules_to_save.append(StationSchedule(**schedule, station=instance))

            return {'save': schedules_to_save, 'update': schedules_to_update}
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as ex:
            print("Exception save schedules, please check it")
            print(ex.args.__str__())
            raise ValueError(str(ex))

    def save_station_address(self, instance, address):
        try:
            data_point = address.pop('point', None)
            point = Point(x=data_point['lng'], y=data_point['lat'])
            address['point'] = point
            return address
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as ex:
            print("Exception save station address, please check it")
            print(ex.args.__str__())
            raise ValueError(str(ex))

    def save_station_services(self, instance, services):
        try:
            services_to_save = []
            services_to_update = []
            for service in services:
                """ Add each service in an array and then save it with the function bulk_create """
                # Search by service and if it exists update instead of create
                station_service = StationService.objects.filter(station=instance, service=service['service'])
                if station_service:
                    sta_service = station_service[0]
                    # Update attributes
                    for field, value in service.items():
                        setattr(sta_service, field, value)
                    # Append to list of service to update
                    services_to_update.append(sta_service)
                    continue

                services_to_save.append(StationService(**service, station=instance))

            return {'save': services_to_save, 'update': services_to_update}
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as ex:
            print("Exception save station services, please check it")
            print(ex.args.__str__())
            raise ValueError(str(ex))

    def save_all_models(self, instance, schedules_to_save, schedules_to_update,
                        services_to_save, services_to_update, address_to_save):

        """ Save all data if everything goes well """
        try:
            instance.save()
            StationSchedule.objects.bulk_create(schedules_to_save)
            StationSchedule.objects.bulk_update(schedules_to_update, fields=["from_hour", "to_hour"])
            StationService.objects.bulk_create(services_to_save)
            StationService.objects.bulk_update(services_to_update, fields=["base_rate_price",
                                                                           'price_kilometer',
                                                                           'from_kilometer',
                                                                           'to_kilometer'])

            if address_to_save:
                address_exist = StationAddress.objects.filter(station=instance)
                # If exist address update attribute and if it not exist create
                if address_exist:
                    station_address = address_exist[0]
                    for field, value in address_to_save.items():
                        setattr(station_address, field, value)
                    station_address.save()
                else:
                    StationAddress(**address_to_save, station=instance).save()

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


# Create a new station
class StationSignUpSerializer(serializers.Serializer):
    """ Serializer only to register a new station """
    username = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='El email ya esta en uso')])

    contact_person = serializers.CharField(max_length=60)
    password = serializers.CharField(min_length=8, max_length=64)
    station_name = serializers.CharField(max_length=100, validators=[UniqueValidator(
        queryset=Station.objects.all(),
        message='Ya existe una central con el mismo nombre. ¿La central es tuya?')])

    def create(self, data):
        try:
            user = User(username=data['username'],
                        is_verified=False,
                        is_client=False,
                        verification_deadline=timezone.now() + timedelta(minutes=20))
            user.set_password(data['password'])
            user.save()
            station = Station.objects.create(user=user,
                                             contact_person=data['contact_person'],
                                             station_name=data['station_name'],
                                             )

            code = generate_verification_token(user=user,
                                               exp=timezone.now() + timedelta(minutes=20),
                                               token_type='email_confirmation')

            subject = 'Bienvenido {name}, Verifica tu cuenta para comenzar'.format(name=station.station_name)
            data = {
                'user': user,
                'token': code,
                'url': settings.URL_SERVER_FRONTEND
            }
            send_email = send_mail_verification(subject=subject,
                                                to_user=user.username,
                                                path_template="emails/users/account_verification.html",
                                                data=data)
            if not send_email:
                raise serializers.ValidationError({'detail': 'Ha ocurrido un error al enviar el correo'})
            return user

        except Exception as ex:
            return serializers.ValidationError({'detail': 'Ha ocurrido un problema al registrarse'})
