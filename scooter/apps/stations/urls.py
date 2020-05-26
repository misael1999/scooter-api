"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.stations.views import stations as station_view
from scooter.apps.stations.views import vehicles as vehicle_view

router = DefaultRouter()
router.register(r'api/v1/stations', station_view.StationViewSet, basename='stations')
router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/vehicles',
                vehicle_view.VehiclesViewSet, basename='vehicles-station')

urlpatterns = [
    # Views
    path('', include(router.urls))
]
