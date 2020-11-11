"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.stations.views import stations as station_view
from scooter.apps.stations.views import delivery_men as station_delivery_view
from scooter.apps.stations.views import vehicles as vehicle_view
from scooter.apps.stations.views import customers as station_customer_view
from scooter.apps.stations.views import notifications as station_notification_view
from scooter.apps.stations.views import zones as station_zone_view

router = DefaultRouter()
router.register(r'api/v1/stations', station_view.StationViewSet, basename='stations')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/vehicles',
                vehicle_view.VehiclesViewSet, basename='vehicles-station')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/delivery_men',
                station_delivery_view.DeliveryMenStationViewSet, basename='delivery-men-station')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/customers',
                station_customer_view.CustomerStationViewSet, basename='customer-station')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/notifications',
                station_notification_view.NotificationStationViewSet, basename='notification-station')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/zones',
                station_zone_view.StationZoneViewSet, basename='zones-station')

urlpatterns = [
    # Views
    path('', include(router.urls))
]
