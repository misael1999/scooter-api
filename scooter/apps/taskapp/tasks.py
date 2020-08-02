# Django
from datetime import timedelta
from django.utils import timezone
# Functions
from scooter.apps.common.models import OrderStatus, Notification
from scooter.apps.delivery_men.models import DeliveryMan
from scooter.utils.functions import send_mail_verification, generate_verification_token
# Celery
from celery.task import task, periodic_task
# FCM
from fcm_django.models import FCMDevice
# Models
from scooter.apps.orders.models import Order
from django.db.models import Q
# Functions
from scooter.utils.functions import send_notification_push_order


@task(name='send_email_task', max_retries=3)
def send_email_task(subject, to_user, path_template, data):
    """ Send email in background """
    send_mail_verification(subject, to_user, path_template, data)


@task(name='send_notification_push_task', max_retries=3)
def send_notification_push_task(user_id, title, body, data):
    """ Send push notifications in all user """
    devices = FCMDevice.objects.filter(user_id=user_id)
    if devices:
        devices.send_message(title=title, body=body, data=data)


@periodic_task(name='reject_orders', run_every=timedelta(minutes=1))
def reject_orders():
    """ Verify orders and reject when nobody responds """
    now = timezone.localtime(timezone.now())
    offset = now + timedelta(seconds=0)
    orders = Order.objects.filter(maximum_response_time__lte=offset,
                                  order_status__slug_name__in=["await_delivery_man", "without_delivery"])
    if orders:
        order_status = OrderStatus.objects.get(slug_name='rejected')
        for order in orders:
            # Function
            send_notification_push_order(order.user_id, title='Pedido rechazado',
                                         body='No hubo respuesta por parte de los repartidores',
                                         data={"type": "REJECT_ORDER",
                                               "order_id": order.id,
                                               "message": "No hubo respuesta del pedid",
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'})
        orders.update(order_status=order_status,
                      reason_rejection="Sin respuesta de los repartidores")


@periodic_task(name='location_notice_not_enabled', run_every=timedelta(minutes=7))
def location_notice_not_enabled():
    """ Notice when the location is not enabled """
    now = timezone.localtime(timezone.now())
    offset = now - timedelta(minutes=7)
    delivery_men = DeliveryMan.objects.filter(delivery_status__slug_name__in=['available', 'busy'],
                                              last_time_update_location__lte=offset)
    for delivery_man in delivery_men:
        send_notification_push_order(delivery_man.user_id, title='¡¡¡¡ Aviso !!!!!',
                                     body='No estamos recibiendo tu ubicación,'
                                          ' por favor desactiva y activa tu disponibilidad',
                                     data={"type": "NOTICE_LOCATION",
                                           "message": "No estamos recibiendo tu ubicación",
                                           'click_action': 'FLUTTER_NOTIFICATION_CLICK'})


@periodic_task(name='disabled_location', run_every=timedelta(hours=1))
def disabled_location():
    """ Disabled location when are available and not send location in several minutes """
    now = timezone.localtime(timezone.now())
    offset = now - timedelta(minutes=50)
    delivery_men = DeliveryMan.objects.filter(delivery_status__slug_name__in=['available', 'busy'],
                                              last_time_update_location__lte=offset)
    for delivery_man in delivery_men:
        send_notification_push_order(delivery_man.user_id, title='¡¡¡¡ Importante !!!!!',
                                     body='Has pasado mucho tiempo sin enviar tu ubicación,'
                                          ' asi que te encuentras fuera de servicio,'
                                          'vuelve activar tu disponibilidad para recibir pedidos',
                                     data={"type": "NOTICE_LOCATION",
                                           "message": "No estamos recibiendo tu ubicación",
                                           'click_action': 'FLUTTER_NOTIFICATION_CLICK'})

    delivery_men.update(delivery_status_id=3)

