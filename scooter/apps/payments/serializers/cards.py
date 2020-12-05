""" Common status serializers """
# Django rest framework
from rest_framework import serializers
# Models
from rest_framework.validators import UniqueValidator
# Models
from scooter.apps.payments.models.cards import Card, CustomerConekta
# Utilities
from scooter.utils.serializers.scooter import ScooterModelSerializer
import conekta

conekta.api_key = "key_2jx7uHTnz8ydRyKkXrNCcQ"
conekta.api_version = "2.0.0"


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
        )

    def create(self, data):
        try:
            customer = self.context['customer']
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
                    source_id=customer_create.payment_sources[0].id
                )
            return data
        except conekta.ConektaError as e:
            print(e.message)
            raise serializers.ValidationError({'detail': str(e.message)})
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in rating order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al guardar la tarjeta'})
