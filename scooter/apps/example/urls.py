""" Clients URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
# from recorcholis.apps.clients import views as view_client

router = DefaultRouter()
# router.register(r'api/v1/stations', view_client.ClientViewSet, basename='clients')

urlpatterns = [
    # Users
    path('', include(router.urls))
]
