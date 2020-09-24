# Django
from datetime import datetime

from asgiref.sync import async_to_sync
from django.contrib.gis.db.models.functions import Distance
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
# JWT
import jwt
# FCM
from fcm_django.models import FCMDevice

from scooter.apps.delivery_men.models import DeliveryMan
from scooter.apps.orders.utils.orders import notify_delivery_men


def send_mail_verification(subject, to_user, path_template, data):
    subject = subject
    from_email = settings.DEFAULT_FROM_EMAIL
    to = to_user
    content = render_to_string(path_template, data)
    try:
        msg = EmailMultiAlternatives(subject, content, from_email, [to])
        msg.attach_alternative(content, "text/html")
        msg.send()
        return True
    except Exception as ex:
        print("Exception sending email, please check it")
        print(str(msg))
        print(ex.args.__str__())
        return False


def generate_verification_token(user, exp, token_type):
    token = jwt.encode({
        'email': user.username,
        'iat': timezone.now(),
        'exp': exp,
        'token_type': token_type
    }, settings.SECRET_KEY, algorithm='HS256')
    return token.decode()


def send_notification_push_order(user_id, title, body, data, sound, android_channel_id):
    devices = FCMDevice.objects.filter(user_id=user_id)
    devices.send_message(title=title, body=body, data=data, sound=sound, android_channel_id=android_channel_id)


def send_notification_push_order_with_sound(user_id, title, body, data, sound, android_channel_id):
    devices = FCMDevice.objects.filter(user_id=user_id)
    if data['type'] == 'NEW_ORDER':
        for device in devices:
            sound_temp = sound
            if device.type == 'ios':
                if sound == 'ringtone.mp3':
                    sound_temp = 'ringtone.aiff'
                else:
                    sound_temp = 'claxon.aiff'
            device.send_message(title=title, body=body, data=data, sound=sound_temp,
                                android_channel_id=android_channel_id)
    else:
        devices.send_message(title=title, body=body, data=data, sound=sound, android_channel_id=android_channel_id)


def get_date_from_querystring(request, date_find, default_value=None):
    if date_find in request.GET:
        from_date_str = request.query_params.get(date_find,
                                                 (timezone.localtime(timezone.now()).date()).strftime('%Y-%m-%d'))
        return datetime.strptime(from_date_str, '%Y-%m-%d')
    else:
        return default_value


def send_order_delivery(location_selected, station, order):
    try:
        # Get nearest delivery man
        delivery_men = get_nearest_delivery_man(location_selected=location_selected, station=station,
                                                list_exclude=[], distance=settings.RANGE_DISTANCE,
                                                status=['available'])

        # Send push notification to delivery_man
        # if delivery_men.count() == 0:
        #     delivery_men = get_nearest_delivery_man(location_selected=location_selected, station=station,
        #                                             list_exclude=[], distance=settings.RANGE_DISTANCE,
        #                                             status=['available', 'busy'])

        if delivery_men.count() == 0:
            delivery_men = get_nearest_delivery_man(location_selected=location_selected, station=station,
                                                    list_exclude=[], distance=settings.RANGE_DISTANCE,
                                                    status=['available', 'busy', 'out_service'])
        for delivery_man in delivery_men:
            user_id = delivery_man.user_id
            send_notification_push_order(user_id=user_id,
                                         title='¡Pedido sin responder!',
                                         body='Hay un pedido nuevo que esta en espera',
                                         sound="ringtone.mp3",
                                         android_channel_id="alarms",
                                         data={"type": "NEW_ORDER",
                                               "order_id": order.id,
                                               "ordering": "",
                                               "message": "Pedido de nuevo",
                                               'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                                               })
        async_to_sync(notify_delivery_men)(order.id, 'NEW_ORDER')

    except ValueError as e:
        print(e.__str__())
        raise ValueError(e)
    except Exception as ex:
        print(ex.args.__str__())
        raise ValueError('Error al mandar notificaciones de pedido')


# Methods helpers
def get_nearest_delivery_man(location_selected, station, list_exclude, distance, status):
    """ Get nearest delivery man and exclude who are in the history of rejected orders """

    # List of delivery men nearest

    # location__distance_lte = (
    #     location_selected.point,
    #     D(km=distance))

    SEARCH_NUMBER_DELIVERY = settings.SEARCH_NUMBER_DELIVERY
    delivery_man = DeliveryMan.objects. \
                       exclude(id__in=list_exclude). \
                       filter(status__slug_name="active", delivery_status__slug_name__in=status, station=station) \
                       .annotate(distance=Distance('location', location_selected)) \
                       .order_by('distance')[:SEARCH_NUMBER_DELIVERY]
    # delivery_man = DeliveryMan.objects.filter(station=station,
    #                                           location__distance_lte=(
    #                                               location_selected.point, D(km=distance))
    #                                           ).exclude(id__in=list_exclude).last()

    return delivery_man
