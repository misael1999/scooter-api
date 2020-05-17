# Django
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
# JWT
import jwt


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
        'email': user.email,
        'iat': timezone.now(),
        'exp': exp,
        'token_type': token_type
    }, settings.SECRET_KEY, algorithm='HS256')
    return token.decode()