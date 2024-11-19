from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis
import json

REDIS_URL = 'redis://127.0.0.1:6379/0'

class EditorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'editor_group'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        shared_content = await self.get_shared_content()  # Get stored contents from Redis
        # Send the current content to the newly connected client
        await self.send(text_data=json.dumps({
            'content': shared_content
        }))

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Get incoming data
        data = json.loads(text_data)
        action = data.get('action')
        username = data.get('username')
        content = data.get('content')

        if action == 'edit':
            await self.save_shared_content(content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'editor_message',
                    'username': username,
                    'content': content
                }
            )

    async def editor_message(self, event):
        # Send the updated content to all clients in the group
        content = event['content']

        await self.send(text_data=json.dumps({
            'content': content
        }))

    async def get_shared_content(self):
        # Use aioredis to create a Redis client
        redis = await aioredis.from_url(REDIS_URL)
        content = await redis.get('shared_content')
        await redis.close()  # Close the Redis connection

        # Decode the bytes to a string, if content is not None
        return content.decode('utf-8') if content is not None else ''

    async def save_shared_content(self, content):
        # Use aioredis to create a Redis client
        redis = await aioredis.from_url(REDIS_URL)
        await redis.set('shared_content', content)
        await redis.close()  # Close the Redis connection
