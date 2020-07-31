""" Function helpers for channels """
# Channels
from channels.layers import get_channel_layer


async def send_order_to_station_channel(station_id, order_id):
    channel_layer = get_channel_layer()
    group_name = 'orders-{id}'.format(id=station_id)
    content = {
        'data': {
            'order_id': order_id,
            'type': 'NEW_ORDER'
        },
    }
    await channel_layer.group_send(
        group_name,
        {"type": "notify", "content": content},
    )


async def notify_station_accept(station_id, order_id):
    channel_layer = get_channel_layer()
    group_name = 'orders-{id}'.format(id=station_id)
    content = {
        'data': {
            'order_id': order_id,
            'type': 'ACCEPT_ORDER'
        },
    }
    await channel_layer.group_send(
        group_name,
        {"type": "notify", "content": content},
    )


async def notify_delivery_men(delivery_man_id, order_id):
    """ Notify all delivery men """
    channel_layer = get_channel_layer()
    group_name = 'delivery-{id}'.format(id=delivery_man_id)
    content = {
        'data': {
            'order_id': order_id,
            'type': 'NEW_ORDER'
        },
    }
    await channel_layer.group_send(
        group_name,
        {"type": "notify_order", "content": content},
    )
