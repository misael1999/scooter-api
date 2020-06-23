""" Function helpers for channels """
# Channels
from channels.layers import get_channel_layer


async def send_order_channel(user, order_id):
    channel_layer = get_channel_layer()
    group_name = 'station-{id}'.format(id=user.id)
    content = {
        'data': {
            'order_id': order_id
        },
    }
    await channel_layer.group_send(
        group_name,
        {"type": "notify", "content": content},
    )
