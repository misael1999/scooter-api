# Order routing
from django.conf.urls import re_path

from .consumers import GeneralOrderConsumer, GeneralDeliveryConsumer

websocket_urlpatterns = [
    re_path(r'^ws/orders/(?P<station_id>\w+)/$', GeneralOrderConsumer, name="general-orders"),
    # Locations
    re_path(r'^ws/stations/(?P<station_id>\w+)/delivery_men/', GeneralDeliveryConsumer, name="general-delivery-man")
]
