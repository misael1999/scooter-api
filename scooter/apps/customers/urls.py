"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.customers.views import customers as customer_view
from scooter.apps.customers.views import addresses as addresses_view

router = DefaultRouter()
router.register(r'api/v1/customers', customer_view.CustomerViewSet, basename='customers')
router.register(r'api/v1/customers/(?P<customer_id>[a-zA-Z0-9_-]+)/addresses',
                addresses_view.CustomerAddressesViewSet, basename='addresses_customer')
urlpatterns = [
    # Views
    path('', include(router.urls))
]
