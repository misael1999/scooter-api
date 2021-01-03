from django.urls import re_path

from scooter.apps.support.consumers.support import SupportStationConsumer

websocket_urlpatterns = [
    re_path(r'^ws/support/(?P<station_id>\w+)/$', SupportStationConsumer, name="support-stations"),
    # re_path(r'^ws/orders/(?P<delivery_man_id>\w+)/delivery_men/$', GeneralDeliveryConsumer,
    #         name="general-orders-delivery"),
    # # Locations
    # # re_path(r'^ws/stations/(?P<station_id>\w+)/delivery_men/', GeneralDeliveryConsumer, name="general-delivery-man"),
    # re_path(r'^ws/customers/(?P<customer_id>\w+)/orders/(?P<order_id>\w+)', GeneralCustomerOrderConsumer,
    #         name="general-customer-order")
]
