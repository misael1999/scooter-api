# Order routing
from django.conf.urls import re_path

from .consumers import OrderConsumer

websocket_urlpatterns = [
    re_path(r'^ws/orders/(?P<station_id>\w+)/$', OrderConsumer, name="orders")
]