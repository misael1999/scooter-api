""" Merchants URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.merchants import views as views


router = DefaultRouter()
router.register(r'api/v1/merchants', views.MerchantViewSet, basename='merchants')

router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/categories',
                views.CategoriesProductsViewSet, basename='categories-merchants')

urlpatterns = [
    # Views
    path('', include(router.urls))
]
