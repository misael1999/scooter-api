"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.customers.views import customers as customer_view

router = DefaultRouter()
router.register(r'api/v1/customers', customer_view.CustomerViewSet, basename='customers')

urlpatterns = [
    # Views
    path('', include(router.urls))
]
