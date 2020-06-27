""" Orders consumer """
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import DenyConnection
from django.contrib.auth.models import AnonymousUser


class OrderConsumer(AsyncJsonWebsocketConsumer):
    """
    This chat consumer handles websocket connections for chat clients.
    It uses AsyncJsonWebsocketConsumer, which means all the handling functions
    must be async functions, and any sync work (like ORM access) has to be
    behind database_sync_to_async or sync_to_async. For more, read
    http://channels.readthedocs.io/en/latest/topics/consumers.html
    """

    # WebSocket event handlers

    async def connect(self):
        self.room_name = 'orders'
        if self.scope['user'] == AnonymousUser():
            raise DenyConnection("Invalid User")

        user = self.scope['user']
        station_id = self.scope['url_route']['kwargs']['station_id']

        if user.station is None:
            self.scope['user'] = AnonymousUser()
            raise DenyConnection("Invalid User")

        if user.station.id != int(station_id):
            self.scope['user'] = AnonymousUser()
            raise DenyConnection("Invalid User")

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

    async def notify(self, event):
        """
        This handles calls elsewhere in this codebase that look
        like:

            channel_layer.group_send(group_name, {
                'type': 'notify',  # This routes it to this handler.
                'content': json_message,
            })

        Don't try to directly use send_json or anything; this
        decoupling will help you as things grow.
        """
        await self.send_json(event["content"])

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Command helper methods called by receive_json
