"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.orders.views import orders as orders_view

router = DefaultRouter()
router.register(r'api/v1/customers/(?P<customer_id>[a-zA-Z0-9_-]+)/orders',
                orders_view.CustomerOrderViewSet, basename='customers_orders')
urlpatterns = [
    # Views
    path('', include(router.urls))
]
