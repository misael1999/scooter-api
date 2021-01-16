"""User URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.orders import views as orders_view
from scooter.apps.orders.views import v2 as orders_view_v2
from scooter.apps.orders.views import v3 as orders_view_v3

router = DefaultRouter()
router.register(r'api/v1/customers/(?P<customer_id>[a-zA-Z0-9_-]+)/orders',
                orders_view.CustomerOrderViewSet, basename='customers_orders')
router.register(r'api/v2/customers/(?P<customer_id>[a-zA-Z0-9_-]+)/orders',
                orders_view_v2.CustomerOrderV2ViewSet, basename='customers_orders_v2')
router.register(r'api/v3/customers/(?P<customer_id>[a-zA-Z0-9_-]+)/orders',
                orders_view_v3.CustomerOrderV3ViewSet, basename='customers_orders_v3')

router.register(r'api/v1/delivery_men/(?P<delivery_man_id>[a-zA-Z0-9_-]+)/orders',
                orders_view.DeliveryMenOrderViewSet, basename='delivery_men_orders')

router.register(r'api/v1/stations/(?P<station_id>[a-zA-Z0-9_-]+)/orders',
                orders_view.StationOrderViewSet, basename='station_orders')
router.register(r'api/v1/merchants/(?P<merchant_id>[a-zA-Z0-9_-]+)/orders',
                orders_view.MerchantOrderViewSet, basename='merchants_orders')
urlpatterns = [
    # Views
    path('', include(router.urls))
]
