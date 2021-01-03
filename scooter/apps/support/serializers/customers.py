""" Common status serializers """
# Django rest framework
import random
from string import ascii_uppercase, digits
from django.conf import settings
from rest_framework import serializers
from scooter.apps.stations.models import Station
from scooter.apps.support.models import Support, SupportMessage
from scooter.apps.support.serializers.support import (SupportModelSimpleSerializer, generate_sku,
                                                      SupportMessageSimpleSerializer)
from scooter.apps.support.utils import send_message
# Django channels
from asgiref.sync import async_to_sync


class CreateSupportModelSerializer(serializers.ModelSerializer):

    text = serializers.CharField(max_length=600)

    class Meta:
        model = Support
        fields = (
            'text',
            'support_type',
            'is_to_order',
            'is_to_help',
            'is_to_delivery_man',
            'delivery_man',
            'station',
            'order'
        )

    def validate(self, data):
        if self.context['is_customer']:
            customer = self.context['customer']
            data['customer'] = customer
        # Verify if the customer has not support open
        support = Support.objects.filter(station=data['station'], customer=data['customer'], support_status_id=1)
        if support.exists():
            raise serializers.ValidationError('Hay un soporte abierto')
        return data

    def create(self, data):
        try:
            customer = data['customer']
            station = data.pop('station', Station.objects.first())
            delivery_man = data.pop('delivery_man', None)
            text = data.pop('text', None)
            request = self.context.get('request', None)
            user = request.user
            is_to_order = data.get('is_to_order', False)
            is_to_help = data.get('is_to_help', False)
            is_to_delivery_man = data.get('is_to_delivery_man', False)

            sku = generate_sku()
            support = Support.objects.create(
                sku=sku,
                customer=customer,
                user=user,
                station=station,
                support_status_id=1,
                **data
            )
            message = SupportMessage.objects.create(text=text,
                                                    support=support,
                                                    sender_by=user,
                                                    receiver_by=station.user if not is_to_delivery_man else delivery_man.user
                                                    )
            message_data = SupportMessageSimpleSerializer(message).data
            # Send push notification to station or delivery man
            # Send data to station or delivery man via socket
            group_name = 'attend-support-{}'.format(station.id)
            async_to_sync(send_message(group_name=group_name, message=message_data))
            # SupportModelSimpleSerializer(support).data
            return {
                'support': "siuuuu"
            }
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create support message, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al guardar el mensaje'})


class CreateMessageSupportSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=600)

    def create(self, data):
        try:
            support = self.context['support']
            is_to_delivery_man = support.is_to_delivery_man
            customer = support.customer
            delivery_man = support.delivery_man
            station = support.station

            # Save message
            message = SupportMessage.objects.create(**data,
                                                    support=support,
                                                    sender_by=customer.user,
                                                    receiver_by=station.user if not is_to_delivery_man else delivery_man.user
                                                    )
            message_data = SupportMessageSimpleSerializer(message).data
            # Send push notification to station or delivery man

            # Send data to station or delivery man via socket
            group_name = 'attend-support-{}'.format(station.id)
            async_to_sync(send_message)(group_name=group_name, message=message_data)
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in create support message, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al guardar el mensaje'})