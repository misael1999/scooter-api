""" Orders consumer """
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import DenyConnection
from django.contrib.auth.models import AnonymousUser
# Models
from scooter.apps.orders.models import Order


# Send when there are new order
from scooter.apps.support.models import Support


class SupportCustomerConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = ''
        self.room_name = 'support-chat'

    async def connect(self):

        if self.scope['user'] == AnonymousUser():
            raise DenyConnection("Invalid User")

        # user = self.scope['user']
        support_id = self.scope['url_route']['kwargs']['support_id']

        self.room_group_name = '{room}-{id}'.format(room=self.room_name, id=support_id)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if self.scope['user'] == AnonymousUser():
            return
        else:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_message_support(self, event):
        await self.send_json(event["content"])

    async def receive_json(self, content, **kwargs):
        print(content)
        pass


class SupportStationConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = ''
        self.room_name = 'attend-support'

    async def connect(self):

        if self.scope['user'] == AnonymousUser():
            raise DenyConnection("Invalid User")

        # user = self.scope['user']
        station_id = self.scope['url_route']['kwargs']['station_id']

        self.room_group_name = '{room}-{id}'.format(room=self.room_name, id=station_id)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if self.scope['user'] == AnonymousUser():
            return
        else:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_message_support(self, event):
        await self.send_json(event["content"])

    async def receive_json(self, content, **kwargs):
        print(content)
        pass