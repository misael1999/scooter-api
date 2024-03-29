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
# merchant products
router.register(r'api/v1/products/(?P<product_id>[a-zA-Z0-9_-]+)/menu_categories',
                views.ProductsMenuCategoryViewSet, basename='categories-merchants')
router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/subcategories',
                views.SubcategoriesProductsViewSet, basename='subcategories-merchants')
router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/products',
                views.ProductsViewSet, basename='products-merchants')
router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/customers',
                views.CustomerMerchantViewSet, basename='customers-merchants')
router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/statistics',
                views.MerchantStatisticsViewSet, basename='statistics-merchants')
router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/delivery_men',
                views.DeliveryMenMerchantViewSet, basename='delivery_men-merchants')
router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/zones',
                views.MerchantZoneViewSet, basename='zones-merchants')
router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/payment_methods',
                views.MerchantPaymentMethodViewSet, basename='payment-methods-merchants')
router.register(r'api/v1/tags',
                views.TagViewSet, basename='tags')
router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/tags',
                views.MerchantTagViewSet, basename='merchant-tags')

urlpatterns = [
    # Views
    path('', include(router.urls))
]
