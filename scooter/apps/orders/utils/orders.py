""" Function helpers for channels """
# Channels
from channels.layers import get_channel_layer


async def send_order_to_station_or_delivery(user):
    channel_layer = get_channel_layer()
    group_name = 'order-{id}'.format(id=user.id)
    await channel_layer.group_send(
        group_name,
        {"type": "notify", "content": 'Hola prro'},
    )
    print('SEND MESSAGE')
