# Django
from datetime import timedelta
from django.utils import timezone
# Functions
from scooter.apps.common.models import OrderStatus
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
    offset = now + timedelta(seconds=30)
    orders = Order.objects.filter(maximum_response_time__lte=offset,
                                  order_status__slug_name="without_delivery")
    if orders:
        order_status = OrderStatus.objects.get(slug_name='rejected')
        orders.update(order_status=order_status,
                      reason_rejection="Sin respuesta")
        for order in orders:
            # Function
            send_notification_push_order(order.user_id, title='Pedido rechazado',
                                         body='No hubo respuesta del pedido',
                                         data={"type": "REJECT_ORDER",
                                               "order_id": order.id,
                                               "message": "No hubo respuesta del pedid",
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'})
