"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.customers.views import customers as customer_view
from scooter.apps.customers.views import addresses as addresses_view
from scooter.apps.customers.views import notifications as notifications_view

router = DefaultRouter()
router.register(r'api/v1/customers', customer_view.CustomerViewSet, basename='customers')
router.register(r'api/v1/customers/(?P<customer_id>[a-zA-Z0-9_-]+)/addresses',
                addresses_view.CustomerAddressesViewSet, basename='addresses_customer')
router.register(r'api/v1/customers/(?P<customer_id>[a-zA-Z0-9_-]+)/notifications',
                notifications_view.NotificationCustomerViewSet, basename='customer_notifications')
router.register(r'api/v1/customers/(?P<customer_id>[a-zA-Z0-9_-]+)/invitations',
                notifications_view.NotificationCustomerViewSet, basename='customer_invitations')
urlpatterns = [
    # Views
    path('', include(router.urls))
]
