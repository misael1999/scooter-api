"""Development settings."""

from .base import *  # NOQA
from .base import env
from datetime import timedelta

# Base
DEBUG = True

# Security
SECRET_KEY = env('DJANGO_SECRET_KEY', default='PB3aGvTmCkzaLGRAxDc3aMayKTPTDd5usT8gw4pCmKOk5AlJjh12pTrnNgQyOHCH')
ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
    "35.236.92.131",
    '127.0.0.1:4200',
    'localhost:4200',
    'scooter-app.team',
    'www.scooter-app.team',
    '192.168.0.6',
    'www.scooterdev.tech',
    'scooterdev.tech',
    '100.25.196.247'
]

CORS_ORIGIN_ALLOW_ALL = True


# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# Templates
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # NOQA

# Email
# EMAIL_HOST = env.str('MAIL_SERVER',)
# EMAIL_PORT = env.int('MAIL_SERVER_PORT')
# EMAIL_HOST_USER = env.str('MAIL_SERVER_USER')
# DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL')
# EMAIL_HOST_PASSWORD = env.str('MAIL_SERVER_PASSWORD')
# EMAIL_USE_TLS = env.bool('MAIL_USE_TLS')
# EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# django-extensions
INSTALLED_APPS += ['django_extensions']  # noqa F405
#
DEFAULT_FROM_EMAIL = env(
    'DJANGO_DEFAULT_FROM_EMAIL',
    default='Scooter<help@scooter-app.team>'
)
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[Scooter envíos]')

# Anymail (Mailgun)
INSTALLED_APPS += ['anymail']  # noqa F405
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
ANYMAIL = {
    'MAILGUN_API_KEY': env('MAILGUN_API_KEY'),
    'MAILGUN_SENDER_DOMAIN': env('MAILGUN_DOMAIN')
}

# Celery
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=2),  # timedelta(minutes=5)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=2),
}

