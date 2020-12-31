""" Common status serializers """
# Django rest framework
from django.conf import settings
from rest_framework import serializers
# Models
from scooter.apps.payments.models.cards import Card, CustomerConekta
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer
import conekta

conekta.api_key = settings.CONEKTA_API_KEY
conekta.api_version = settings.CONEKTA_API_VERSION


class CardSimpleSerializer(ScooterModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'


class CardModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'
        read_only_fields = (
            'customer_conekta',
            'customer',
            'conekta_id',
            'source_id',
            'status'
        )

    def create(self, data):
        try:
            customer = self.context['customer']
            card_exist = Card.objects.filter(customer=customer,
                                             last_four=data['last_four'],
                                             status=1)
            if card_exist.exists():
                raise ValueError('Ya existe una tarjeta con la misma terminación')
            # Comprobar si existe el usuario
            customer_exist = CustomerConekta.objects.filter(customer=customer)

            if customer_exist.exists():
                customer_conek = customer_exist[0]
                # Buscamos al usuario en la base de datos de conekta
                customer_update = conekta.Customer.find(customer_conek.customer_conekta_id)

                # Añadimos un nuevo metodo de pago
                source = customer_update.createPaymentSource({
                    'type': 'card',
                    'token_id': data['card_token']
                })

                # Añadimos un nueva tarjeta en nuestra base de datos
                card = Card.objects.create(
                    customer_conekta=customer_conek,
                    customer=customer,
                    conekta_id=customer_update.id,
                    **data,
                    source_id=source.id
                )

            else:
                # Si no existe creamos un nuevo usuario y tarjeta
                customer_create = conekta.Customer.create({
                    'name': customer.name,
                    'email': customer.user.username,
                    'phone': customer.phone_number,
                    'payment_sources': [{
                        'type': 'card',
                        'token_id': data['card_token']
                    }]
                })

                # Añadimos el usuario a nuestra base de datos
                customer_conekta = CustomerConekta.objects.create(
                    user=customer.user,
                    customer=customer,
                    customer_conekta_id=customer_create.id
                )
                # Creamos la tarjeta en nuestra base de datos
                card = Card.objects.create(
                    customer_conekta=customer_conekta,
                    customer=customer,
                    **data,
                    conekta_id=customer_create.id,
                    source_id=customer_create.payment_sources[0].id
                )
            return data
        except conekta.ConektaError as e:
            print('CONEKTA ERROR')
            print(e.message)
            raise serializers.ValidationError({'detail': 'Tarjeta invalida'})
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in rating order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al guardar la tarjeta'})


class UpdateCardSerializer(serializers.Serializer):

    cvv = serializers.IntegerField()

    def update(self, card, data):
        try:
            customer = conekta.Customer.find(card.conekta_id)
            customer.payment_sources[0].update({'cvv': data['cvv']})
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in rating order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al guardar la tarjeta'})