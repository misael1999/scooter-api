from django.urls import re_path

from scooter.apps.support.consumers.support import SupportStationConsumer
from scooter.apps.support.consumers.support import SupportCustomerConsumer

websocket_urlpatterns = [
    re_path(r'^ws/support/(?P<station_id>\w+)/$', SupportStationConsumer, name="support-stations"),
    re_path(r'^ws/support-chat/(?P<support_id>\w+)/$', SupportCustomerConsumer, name="support-connect")
]
