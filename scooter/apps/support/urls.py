""" Support URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.support import views

router = DefaultRouter()
router.register(r'api/v1/customers/(?P<customer_id>[a-zA-Z0-9_-]+)/support',
                views.CustomerSupportViewSet, basename='customers_support')
router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/support',
                views.StationSupportViewSet, basename='stations_support')
router.register(r'api/v1/support/(?P<support_id>[a-zA-Z0-9_-]+)/messages',
                views.SupportMessageViewSet, basename='support_messages')
urlpatterns = [
    # Users
    path('', include(router.urls))
]
