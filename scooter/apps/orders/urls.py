"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
router = DefaultRouter()
urlpatterns = [
    # Views
    path('', include(router.urls))
]
