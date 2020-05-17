""" Common URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.common.views import status as status_view

router = DefaultRouter()
router.register(r'api/v1/commons', status_view.StatusViewSet, basename='common')

urlpatterns = [
    # Users
    path('', include(router.urls))
]
