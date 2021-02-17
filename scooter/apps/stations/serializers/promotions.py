# Rest framework
from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
# Models
from scooter.apps.customers.models import CustomerPromotion, Customer
from scooter.utils.functions import send_notification_push_order_with_sound


class CreateCustomerPromotionSerializer(serializers.Serializer):
    """ Create Free Delivery to customers"""
    customer_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Customer.objects.all())
    quantity_days_validity = serializers.IntegerField()

    def create(self, data):
        try:
            customers = data['customer_ids']
            customer_promotion_to_save = []
            days = data['quantity_days_validity']
            now = timezone.localtime(timezone.now())
            for customer in customers:
                promotion = CustomerPromotion.objects.create(
                    name="Envío gratis",
                    description="Tienes un envío gratis, para utilizarlo en tu proxíma compra ",
                    customer=customer,
                    history=None,
                    created_at=now,
                    expiration_date=now + timedelta(days=days)
                )
                # Send push to customers
                send_notification_push_order_with_sound(user_id=customer.user_id,
                                                        title='Tienes un envío gratis',
                                                        body='Ha recibido un cupón para un envío gratis',
                                                        sound="claxon.mp3",
                                                        android_channel_id="claxon",
                                                        data={"type": "FREE_DELIVERY",
                                                              "order_id": customer.id,
                                                              "message": "Pedido de nuevo",
                                                              'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                              })
            return data
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception create customer promotions, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al consultar los repartidores'})
