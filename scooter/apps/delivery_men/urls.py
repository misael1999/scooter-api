"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.delivery_men import views as delivery_view


router = DefaultRouter()
router.register(r'api/v1/delivery_men',
                delivery_view.DeliveryMenViewSet, basename='delivery-men')
urlpatterns = [
    # Views
    path('', include(router.urls))
]
