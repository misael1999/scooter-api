""" Orders consumer """
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import DenyConnection
from django.contrib.auth.models import AnonymousUser
# Models
from scooter.apps.orders.models import Order

# Send when there are new order
class GeneralOrderConsumer(AsyncJsonWebsocketConsumer):

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
        await self.send_json(event["content"])


# Check when a delivery man change his location
class GeneralDeliveryConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.room_name = 'orders'
        if self.scope['user'] == AnonymousUser():
            raise DenyConnection("Invalid User")

        user = self.scope['user']
        delivery_man_id = self.scope['url_route']['kwargs']['delivery_man_id']

        if user.deliveryman is None:
            self.scope['user'] = AnonymousUser()
            raise DenyConnection("Invalid User")

        if user.deliveryman.id != int(delivery_man_id):
            self.scope['user'] = AnonymousUser()
            raise DenyConnection("Invalid User")

        self.room_group_name = '{room}'.format(room=self.room_name)
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

    async def notify_order(self, event):
        await self.send_json(event["content"])


class GeneralCustomerOrderConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):

        self.room_name = 'order'
        if self.scope['user'] == AnonymousUser():
            raise DenyConnection("Invalid User")

        user = self.scope['user']
        customer_id = self.scope['url_route']['kwargs']['customer_id']
        order_id = self.scope['url_route']['kwargs']['order_id']

        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            self.scope['user'] = AnonymousUser()
            raise DenyConnection("Invalid User")

        if user.customer is None:
            self.scope['user'] = AnonymousUser()
            raise DenyConnection("Invalid User")

        if order.user_id != int(user.id):
            self.scope['user'] = AnonymousUser()
            raise DenyConnection("Invalid User")

        if user.customer.id != int(customer_id):
            self.scope['user'] = AnonymousUser()
            raise DenyConnection("Invalid User")

        self.room_group_name = '{room}-{id}'.format(room=self.room_name, id=customer_id)
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

    async def notify_order_status(self, event):
        await self.send_json(event["content"])

