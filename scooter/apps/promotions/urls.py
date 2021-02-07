""" Clients URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.promotions import views

router = DefaultRouter()
router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/promotions',
                views.MerchantPromotionViewSet, basename='promotions-merchants')
urlpatterns = [
    # Users
    path('', include(router.urls))
]
