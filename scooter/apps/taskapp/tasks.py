# Django
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
# Functions
from scooter.apps.common.models import OrderStatus
from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.merchants.models import Merchant, MerchantSchedule
from scooter.utils.functions import send_mail_verification, send_order_delivery, return_money_user, \
    send_notification_push_order_with_sound
# Celery
from celery.task import task, periodic_task
from celery.schedules import crontab

# FCM
from fcm_django.models import FCMDevice
# Models
from scooter.apps.orders.models import Order
# Functions
from scooter.utils.functions import send_notification_push_order
from scooter.utils.functions import send_notice_order_delivery_fn


@task(name='send_email_task', max_retries=3)
def send_email_task(subject, to_user, path_template, data):
    """ Send email in background """
    send_mail_verification(subject, to_user, path_template, data)


# @task(name='send_email_order', max_retries=3)
# def send_email_delivr(subject, to_user, path_template, data):
#     """ Send email in background when order is delivered """
#     send_mail_verification(subject, to_user, path_template, data)


@task(name='send_notification_push_task', max_retries=3)
def send_notification_push_task(user_id, title, body, data, android_channel_id, sound):
    """ Send push notifications in all user """
    devices = FCMDevice.objects.filter(user_id=user_id)
    if devices:
        devices.send_message(title=title, body=body, data=data, sound=sound,
                             android_channel_id=android_channel_id, )


@task(name='send_notice_order_delivery', max_retries=3)
def send_notice_order_delivery(order_id):
    order = Order.objects.get(pk=order_id)
    """ Send push notifications in all delivery  """
    send_notice_order_delivery_fn(location_selected=order.merchant_location,
                                  station=order.station,
                                  order=order)


@periodic_task(name='send_notification_delivery', run_every=timedelta(minutes=2))
def send_notification_delivery():
    """ Send notification delivery man when nobody response """
    # now = timezone.localtime(timezone.now())
    # offset = now - timedelta(seconds=90)
    # orders = Order.objects.filter(order_ready_date__lte=offset,
    #                               order_status__slug_name__in=["await_delivery_man"])
    orders = Order.objects.filter(order_status__slug_name__in=["await_delivery_man"])
    # orders = Order.objects.filter(Q(order_ready_date__lte=offset,
    #                                 order_status__slug_name__in=["await_delivery_man"]
    #                                 ) | Q(order_status__slug_name__in=["await_delivery_man"],
    #                                       maximum_response_time__lte=offset,
    #                                       merchant=None,
    #                                       ))
    if orders:
        for order in orders:
            station = order.station
            if station.assign_delivery_manually:
                send_notification_push_order(user_id=station.user_id,
                                             title='¡¡¡¡¡ Pedido SIN responder !!!!!!!',
                                             body='Tienes un pedido sin responder',
                                             sound="alarms.mp3",
                                             android_channel_id="alarms",
                                             data={"type": "NEW_ORDER",
                                                   "order_id": order.id,
                                                   "message": "Pedido de nuevo",
                                                   'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                                   })
            else:
                send_order_delivery(location_selected=order.merchant_location,
                                    station=order.station,
                                    order=order)


# Period Task with crontab
@periodic_task(name='close_or_open_merchants',
               run_every=crontab(minute=2, hour='8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23'))
def open_or_close_merchants():
    today = timezone.localtime().strftime("%A").lower()
    now = timezone.localtime(timezone.now())
    offset = now
    current_hour = offset.strftime('%H:%M:%S')
    merchants_to_update = []
    merchants = Merchant.objects.filter(status_id=1)
    for merchant in merchants:
        try:
            merchant_schedule = merchant.schedules.get(schedule_name=today, status_id=1, is_open=True)
            from_hour = str(merchant_schedule.from_hour)
            to_hour = str(merchant_schedule.to_hour)
            # Abrir comercio
            if current_hour >= from_hour and current_hour < to_hour:
                merchant.is_open = True
                merchants_to_update.append(merchant)
            else:
                merchant.is_open = False
                merchants_to_update.append(merchant)
        except MerchantSchedule.DoesNotExist:
            merchant.is_open = False
            merchants_to_update.append(merchant)
    Merchant.objects.bulk_update(merchants_to_update, ['is_open'])

    # @periodic_task(name='reject_orders', run_every=timedelta(minutes=1))


# def reject_orders():
#     """ Verify orders and reject when nobody responds """
#     now = timezone.localtime(timezone.now())
#     offset = now + timedelta(seconds=0)
#     orders = Order.objects.filter(maximum_response_time__lte=offset,
#                                   merchant=None,
#                                   order_status__slug_name__in=["await_delivery_man", "without_delivery"])
#     if orders:
#         order_status = OrderStatus.objects.get(slug_name='rejected')
#         for order in orders:
#             # Function
#             send_notification_push_order(order.user_id, title='Pedido rechazado',
#                                          body='No hubo respuesta por parte de los repartidores',
#                                          sound="default",
#                                          android_channel_id="messages",
#                                          data={"type": "REJECT_ORDER",
#                                                "order_id": order.id,
#                                                "message": "No hubo respuesta del pedido",
#                                                'click_action': 'FLUTTER_NOTIFICATION_CLICK'})
#         orders.update(order_status=order_status,
#                       reason_rejection="Pedido ignorado por el central")


@periodic_task(name='ignore_orders', run_every=timedelta(minutes=1))
def ignore_orders():
    """ Verify orders and reject when nobody responds """
    now = timezone.localtime(timezone.now())
    offset = now + timedelta(seconds=0)
    orders = Order.objects.filter(maximum_response_time__lte=offset,
                                  order_status__slug_name__in=["await_confirmation_merchant"])
    if orders:
        order_status = OrderStatus.objects.get(slug_name='ignored')
        for order in orders:
            type_notification = 'REJECT_ORDER_MERCHANT'
            if order.is_payment_online:
                # Devolver el dinero
                type_notification = 'REJECT_ORDER_MERCHANT_PAYMENT'
                return_money_user(order)
            else:
                # Function
                send_notification_push_order(order.user_id, title='Pedido ignorado por el comerciante',
                                             body='No hubo respuesta por parte del comercio',
                                             sound="default",
                                             android_channel_id="messages",
                                             data={"type": type_notification,
                                                   "order_id": order.id,
                                                   "message": "No hubo respuesta del comerciante",
                                                   'click_action': 'FLUTTER_NOTIFICATION_CLICK'})
        orders.update(order_status=order_status,
                      in_process=False,
                      reason_rejection="Pedido ignorado por el comercio")

# @periodic_task(name='location_notice_not_enabled', run_every=timedelta(hours=2))
# def location_notice_not_enabled():
#     """ Notice when the location is not enabled """
#     now = timezone.localtime(timezone.now())
#     offset = now - timedelta(minutes=20)
#     delivery_men = DeliveryMan.objects.filter(delivery_status__slug_name__in=['available', 'busy'],
#                                               last_time_update_location__lte=offset)
#     for delivery_man in delivery_men:
#         send_notification_push_order(delivery_man.user_id, title='¡¡¡¡ Aviso !!!!!',
#                                      android_channel_id="locations",
#                                      sound="default",
#                                      body='No estamos recibiendo tu ubicación,'
#                                           ' por favor desactiva y activa tu disponibilidad',
#                                      data={"type": "NOTICE_LOCATION",
#                                            "message": "No estamos recibiendo tu ubicación",
#                                            'click_action': 'FLUTTER_NOTIFICATION_CLICK'})

# @periodic_task(name='disabled_location', run_every=timedelta(hours=2))
# def disabled_location():
#     """ Disabled location when are available and not send location in several minutes """
#     now = timezone.localtime(timezone.now())
#     offset = now - timedelta(minutes=30)
#     delivery_men = DeliveryMan.objects.filter(delivery_status__slug_name__in=['available', 'busy'],
#                                               last_time_update_location__lte=offset)
#     for delivery_man in delivery_men:
#         send_notification_push_order(delivery_man.user_id, title='¡¡¡¡ Importante !!!!!',
#                                      body='Has pasado mucho tiempo sin enviar tu ubicación,'
#                                           'vuelve activar tu disponibilidad para recibir pedidos',
#                                      sound="default",
#                                      android_channel_id="locations",
#                                      data={"type": "NOTICE_LOCATION",
#                                            "message": "No estamos recibiendo tu ubicación",
#                                            'click_action': 'FLUTTER_NOTIFICATION_CLICK'})

# delivery_men.update(delivery_status_id=3)
