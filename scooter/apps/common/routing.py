# Order routing
from django.conf.urls import re_path

from .consumers import GeneralOrderConsumer, GeneralDeliveryConsumer, GeneralCustomerOrderConsumer

websocket_urlpatterns = [
    re_path(r'^ws/orders/(?P<station_id>\w+)/$', GeneralOrderConsumer, name="general-orders"),
    re_path(r'^ws/orders/(?P<delivery_man_id>\w+)/delivery_men/', GeneralDeliveryConsumer, name="general-orders"),
    # Locations
    # re_path(r'^ws/stations/(?P<station_id>\w+)/delivery_men/', GeneralDeliveryConsumer, name="general-delivery-man"),
    re_path(r'^ws/customers/(?P<customer_id>\w+)/orders/(?P<order_id>\w+)', GeneralCustomerOrderConsumer,
            name="general-customer-order")
]
