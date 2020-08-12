""" Merchants URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.merchants import views as views


router = DefaultRouter()
router.register(r'api/v1/merchants', views.MerchantViewSet, basename='merchants')

# router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/vehicles',
#                 vehicle_view.VehiclesViewSet, basename='vehicles-station')

urlpatterns = [
    # Views
    path('', include(router.urls))
]
