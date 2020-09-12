# Django
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
# JWT
import jwt
# FCM
from fcm_django.models import FCMDevice


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
    sound = 'ringtone.mp3'
    devices.send_message(title=title, body=body, data=data, sound=sound, android_channel_id=android_channel_id)


def send_notification_push_order_with_sound(user_id, title, body, data, sound, android_channel_id):
    devices = FCMDevice.objects.filter(user_id=user_id)
    if data['type'] == 'NEW_ORDER':
        for device in devices:
            if device.type == 'ios':
                if sound == 'ringtone.mp3':
                    sound = 'ringtone.aiff'
                else:
                    sound = 'claxon.aiff'
            device.send_message(title=title, body=body, data=data, sound=sound,
                                android_channel_id="alarms")
    else:
        if devices:
            devices.send_message(title=title, body=body, data=data, sound=sound, android_channel_id=android_channel_id)


def get_date_from_querystring(request, date_find, default_value=None):
    if date_find in request.GET:
        from_date_str = request.query_params.get(date_find,
                                                 (timezone.localtime(timezone.now()).date()).strftime('%Y-%m-%d'))
        return datetime.strptime(from_date_str, '%Y-%m-%d')
    else:
        return default_value
