""" Function helpers for channels """
# Channels
from channels.layers import get_channel_layer


async def send_notify_change_location(station_id, delivery_id, type_data):
    channel_layer = get_channel_layer()
    group_name = 'delivery-{id}'.format(id=station_id)
    content = {
        'data': {
            'delivery_id': delivery_id,
            'type': type_data
        },
    }
    await channel_layer.group_send(
        group_name,
        {"type": "notify_location", "content": content},
    )
