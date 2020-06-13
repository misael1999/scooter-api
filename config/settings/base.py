"""Base settings to build other settings files upon."""

import environ
import os
from .constants import *

ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR_2 = ROOT_DIR.path('scooter/apps')
APPS_DIR = ROOT_DIR.path('scooter')

root = environ.Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env = environ.Env(DEBUG=(bool, False), )
environ.Env.read_env()

# Base
DEBUG = env.bool('DJANGO_DEBUG', False)

# Language and timezone
TIME_ZONE = 'America/Mexico_City'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

# DATABASES

DATABASES = {
    'default': env.db()
}

DATABASES['default']['ATOMIC_REQUESTS'] = True

# URLs
ROOT_URLCONF = 'config.urls'

# WSGI
WSGI_APPLICATION = 'config.wsgi.application'

# ASGI
ASGI_APPLICATION = 'config.settings.routing.application'

# USERS AND AUTHENTICATION
AUTH_USER_MODEL = 'users.User'

# Apps
DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.gis',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'swagger_ui',
    'corsheaders',
    'rest_framework_gis',
    'channels',
    'fcm_django'
]
LOCAL_APPS = [
    'scooter.apps.users.apps.UsersAppConfig',
    'scooter.apps.common.apps.CommonsAppConfig',
    'scooter.apps.delivery_men.apps.DeliverMenAppConfig',
    'scooter.apps.customers.apps.CustomersAppConfig',
    'scooter.apps.stations.apps.StationsAppConfig',
    'scooter.apps.orders.apps.OrdersAppConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Passwords
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    }
]

# Middlewares
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Static files
STATIC_ROOT = str(ROOT_DIR('static'))
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media
MEDIA_ROOT = str(APPS_DIR('media'))
MEDIA_URL = '/media/'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Security
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Email
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# Admin
ADMIN_URL = 'admin/'
ADMINS = [
    ("""Misael Gonzalez""", 'misael@gmail.com'),
]
MANAGERS = ADMINS

# Celery
INSTALLED_APPS += ['scooter.apps.taskapp.celery.CeleryAppConfig']
if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 60

redis_host = os.environ.get('REDIS_HOST', '127.0.0.1')

# Channel layer definitions
# http://channels.readthedocs.io/en/latest/topics/channel_layers.html
CHANNEL_LAYERS = {
    "default": {
        # This example app uses the Redis channel layer implementation channels_redis
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(redis_host, 6379)],
        },
    },
}

# Django rest framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    # Parser classes priority-wise for Swagger
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'EXCEPTION_HANDLER': 'scooter.utils.custom_handler_error.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 15
}

FCM_DJANGO_SETTINGS = {
    "APP_VERBOSE_NAME": "Scooter",
    # default: _('FCM Django')
    "FCM_SERVER_KEY": "AAAAg9bmMBM:APA91bHJiRLZfMs9U5Nm-9ovjIy1iEyI7ewEb_b9MBAe--6L3ZqvOg8tpCp3hUmAtUoCf2SpkT55iXAjEXbZ8ZWpa6NIdIAG9JcgFfXMiQk1FGK_u5g4PRsk6LzA6blsYa5t8Fl0W2QM",
    # true if you want to have only one active device per registered user at a time
    # default: False
    "ONE_DEVICE_PER_USER": False,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": False,
}

# Swagger
SWAGGER_YAML_FILE = str(APPS_DIR.path('swagger.yaml'))  # os.path.join(BASE_DIR, 'swagger.yaml')
FACEBOOK_APP_ID = '690189338433902'
FACEBOOK_APP_SECRET = '4c55431b063952e631df380e0e73a10a'
