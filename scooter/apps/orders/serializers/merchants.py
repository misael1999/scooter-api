# Rest framework
from rest_framework import serializers
# Serializers
# Models
from scooter.apps.common.models import OrderStatus
from scooter.apps.delivery_men.models import DeliveryMan
# Functions channels
# Functions
from scooter.apps.merchants.models import Product
from scooter.apps.orders.serializers import send_order_delivery
from scooter.apps.orders.serializers.orders import get_nearest_delivery_man
# Serializers primary field
from scooter.apps.common.serializers.common import StationFilteredPrimaryKeyRelatedField
# Task Celery
from scooter.apps.taskapp.tasks import send_notification_push_task
from scooter.utils.functions import send_notification_push_order


class AcceptOrderMerchantSerializer(serializers.Serializer):

    def update(self, order, data):
        try:
            merchant = self.context['merchant']
            if order.order_status.slug_name is 'preparing_order':
                raise ValueError('El pedido ya fue aceptado')
            if order.order_status.slug_name in ['ignored', 'rejected', 'cancelled']:
                raise ValueError('El pedido fue ignorado o rechazado')

            order_status = OrderStatus.objects.get(slug_name="preparing_order")
            order.order_status = order_status
            order.in_process = True
            order.save()
            # details = order.details.all()
            # products_to_update = []
            # for detail in details:
            #     product = Product.objects.get(pk=detail.product_id)
            #     product.stock = product.stock - detail.quantity
            #     products_to_update.append(product)
            #
            # Product.objects.bulk_update(products_to_update, fields=['stock'])
            # Update stock
            # product.save()
            send_notification_push_order(user_id=order.user_id,
                                         title='{} esta preparando tu pedido'.format(merchant.merchant_name),
                                         body='Te avisaremos cuando lo tenga listo',
                                         sound="default",
                                         android_channel_id="messages",
                                         data={"type": "MERCHANT_ACCEPTED_ORDER",
                                               "order_id": order.id,
                                               "message": "Preparando pedido",
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                               })
            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            print("Exception in accept order, please check it")
            print(ex.args.__str__())
            raise serializers.ValidationError({'detail': 'Error al aceptar el pedido'})


class RejectOrderMerchantSerializer(serializers.Serializer):
    reason_rejection = serializers.CharField(max_length=100, required=True, allow_null=True)

    def update(self, order, data):
        merchant = self.context['merchant']
        order_status = OrderStatus.objects.get(slug_name="rejected")
        order.order_status = order_status
        order.reason_rejection = data['reason_rejection']
        order.in_process = False
        order.save()
        send_notification_push_order(user_id=order.user_id,
                                     title='{} ha rechazado tu pedido'.format(merchant.merchant_name),
                                     body='{}'.format(data['reason_rejection']),
                                     sound="default",
                                     android_channel_id="messages",
                                     data={"type": "REJECT_ORDER",
                                           "order_id": order.id,
                                           "message": "Pedido rechazado",
                                           'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                           })
        return order


class CancelOrderMerchantSerializer(serializers.Serializer):
    reason_rejection = serializers.CharField(max_length=100, required=True, allow_null=True)

    def update(self, order, data):
        merchant = self.context['merchant']
        order_status = OrderStatus.objects.get(slug_name="cancelled")
        order.order_status = order_status
        order.reason_rejection = data['reason_rejection']
        order.in_process = False
        order.save()
        send_notification_push_order(user_id=order.user_id,
                                     title='{} ha cancelado tu pedido'.format(merchant.merchant_name),
                                     body='{}'.format(data['reason_rejection']),
                                     sound="default",
                                     android_channel_id="messages",
                                     data={"type": "REJECT_ORDER",
                                           "order_id": order.id,
                                           "message": "Pedido cancelado",
                                           'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                           })
        return order


class OrderReadyMerchantSerializer(serializers.Serializer):

    def update(self, order, data):
        try:
            merchant = self.context['merchant']
            if not merchant.is_delivery_by_store:
                order_status = OrderStatus.objects.get(slug_name="await_delivery_man")
                order.order_status = order_status
                order.save()
                send_order_delivery(location_selected=merchant.point,
                                    station=order.station,
                                    order=order)
                send_notification_push_order(user_id=order.user_id,
                                             title='Tu pedido de {} esta listo'.format(merchant.merchant_name),
                                             body='Estamos buscando al repartidor más cercano',
                                             sound="default",
                                             android_channel_id="messages",
                                             data={"type": "ORDER_READY",
                                                   "order_id": order.id,
                                                   "message": "Pedido listo para ser recogido",
                                                   'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                   })
            return order
        except ValueError as e:
            raise serializers.ValidationError({'details': str(e)})
        except Exception as ex:
            raise serializers.ValidationError({'details': 'Ha ocurrido un error desconocido'})

