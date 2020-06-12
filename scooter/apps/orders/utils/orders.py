""" Function helpers for channels """
# Channels
from channels.layers import get_channel_layer


async def send_order(user, order):
    channel_layer = get_channel_layer()
    group_name = 'order-{id}'.format(id=user.id)
    content = {
        'data': order,
    }
    await channel_layer.group_send(
        group_name,
        {"type": "notify", "content": content},
    )
    print('SEND MESSAGE')
