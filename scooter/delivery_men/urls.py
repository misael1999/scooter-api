"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.users.views import users as user_view
from scooter.users.views import customers as customer_view
from scooter.users.views import stations as station_view


router = DefaultRouter()
router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/delivery_men',
                customer_view.CustomerViewSet, basename='products-merchants')
urlpatterns = [
    # Views
    path('', include(router.urls))
]
