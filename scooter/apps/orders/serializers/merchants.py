# Rest framework
from django.utils import timezone
from rest_framework import serializers
from scooter.apps.common.models import OrderStatus
from scooter.apps.orders.serializers import send_order_delivery
from scooter.utils.functions import send_notification_push_order


class AcceptOrderMerchantSerializer(serializers.Serializer):

    def validate(self, data):
        order = self.context['order']
        merchant = self.context['merchant']

        if order.order_status.slug_name in ['rejected', 'ignored']:
            raise serializers.ValidationError({'detail': 'El pedido fue ignorado o rechazado,'
                                                         ' el tiempo de espera culmino'},
                                              code='order')

        # Verify that the order does not have a delivery man assigned
        if order.order_status.slug_name not in ['await_confirmation_merchant']:
            raise serializers.ValidationError({'detail': 'El pedido ya fue aceptado'},
                                              code='order_already')
        data['order'] = order
        data['merchant'] = merchant

        return data

    def update(self, order, data):
        try:
            merchant = data['merchant']
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
        try:
            merchant = self.context['merchant']
            print(order.order_status.slug_name)
            if order.order_status.slug_name != 'await_confirmation_merchant':
                raise ValueError('El pedido ya fue aceptado o rechazado')
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
                                         data={"type": "REJECT_ORDER_MERCHANT",
                                               "order_id": order.id,
                                               "message": "Pedido rechazado",
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                               })
            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            raise serializers.ValidationError({'detail': 'Error desconocido'})


class CancelOrderMerchantSerializer(serializers.Serializer):
    reason_rejection = serializers.CharField(max_length=100, required=True, allow_null=True)

    def update(self, order, data):
        try:
            merchant = self.context['merchant']
            if order.order_status.slug_name not in ['await_confirmation_merchant', 'preparing_order']:
                raise ValueError('No es posible cancelar pedido, verifique que no haya sido aceptado o cancelado')
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
                                         data={"type": "REJECT_ORDER_MERCHANT",
                                               "order_id": order.id,
                                               "message": "Pedido cancelado",
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                               })
            return order
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            raise serializers.ValidationError({'detail': 'Error desconocido'})


class OrderReadyMerchantSerializer(serializers.Serializer):

    def update(self, order, data):
        try:
            merchant = self.context['merchant']
            if not merchant.is_delivery_by_store:
                order_status = OrderStatus.objects.get(slug_name="await_delivery_man")
                order.order_status = order_status
                order.order_ready_date = timezone.localtime(timezone.now())
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
