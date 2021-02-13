"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.stations import views


router = DefaultRouter()
router.register(r'api/v1/stations', views.StationViewSet, basename='stations')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/customer_promotions',
                views.StationCustomerPromotionViewSet, basename='customer-promotions-station')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/vehicles',
                views.VehiclesViewSet, basename='vehicles-station')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/merchants',
                views.MerchantStationViewSet, basename='merchants-station')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/delivery_men',
                views.DeliveryMenStationViewSet, basename='delivery-men-station')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/customers',
                views.CustomerStationViewSet, basename='customer-station')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/notifications',
                views.NotificationStationViewSet, basename='notification-station')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/zones',
                views.StationZoneViewSet, basename='zones-station')

urlpatterns = [
    # Views
    path('', include(router.urls))
]
