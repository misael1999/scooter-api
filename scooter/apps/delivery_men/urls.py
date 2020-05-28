"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.delivery_men import views as station_view


router = DefaultRouter()
router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/delivery_men',
                station_view.DeliveryMenStationViewSet, basename='delivery-men-station')

router.register(r'api/v1/delivery_men',
                station_view.DeliveryMenViewSet, basename='delivery-men')
urlpatterns = [
    # Views
    path('', include(router.urls))
]
