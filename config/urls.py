"""Main URLs module."""

from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter
# Devices FCM
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

router = DefaultRouter()

router.register(r'api/v1/devices', FCMDeviceAuthorizedViewSet)

urlpatterns = [
    # Django Admin
    path('', include('swagger_ui.urls')),
    path(settings.ADMIN_URL, admin.site.urls),
    # Devices FCM
    path('', include(router.urls)),
    #  Apps Urls
    # Users
    path('', include('scooter.apps.users.urls')),
    # Common
    path('', include('scooter.apps.common.urls')),
    # Delivery men
    path('', include('scooter.apps.delivery_men.urls')),
    # Orders
    path('', include('scooter.apps.orders.urls')),
    # Customers
    path('', include('scooter.apps.customers.urls')),
    # Stations
    path('', include('scooter.apps.stations.urls')),
    # Merchants
    path('', include('scooter.apps.merchants.urls')),
    # Marketing
    path('', include('scooter.apps.marketing.urls')),
    # Payments
    path('', include('scooter.apps.payments.urls')),
    # Support
    path('', include('scooter.apps.support.urls')),
    # Promotions
    path('', include('scooter.apps.promotions.urls'))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
