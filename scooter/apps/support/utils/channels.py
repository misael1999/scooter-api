""" Function helpers for channels """
# Channels
from channels.layers import get_channel_layer


async def send_message(group_name, message):
    channel_layer = get_channel_layer()
    # group_name = 'support-{id}'.format(id=station_id)
    content = {
        'data': {
            'message': message,
            'type': 'NEW_MESSAGE_SUPPORT'
        },
    }
    await channel_layer.group_send(
        group_name,
        {"type": "send_message_support", "content": content},
    )
