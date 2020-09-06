""" Merchants URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.marketing import views as views


router = DefaultRouter()
router.register(r'api/v1/marketing', views.MarketerViewSet, basename='marketing')

urlpatterns = [
    # Views
    path('', include(router.urls))
]
