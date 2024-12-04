from channels.generic.websocket import AsyncWebsocketConsumer
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
import redis.asyncio as aioredis
import json, environ, pymongo

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env_file = BASE_DIR / ".env"
environ.Env.read_env(env_file=env_file)

REDIS_URL = 'redis://127.0.0.1:6379/0'

class EditorConsumer(AsyncWebsocketConsumer):
    # Connect to MongoDB            
    DATABASE_URL = env('DATABASE_URL')
    db_name = env('db_name')
    db_collection = env('db_collection')

    client = pymongo.MongoClient(DATABASE_URL)
    db = client[db_name]
    collection = db[db_collection] 

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
            'content': shared_content,
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
        elif action == 'save':
            await self.save_db(username, content)


    async def editor_message(self, event):
        # Send the updated content to all clients in the group
        content = event['content']
        username = event['username']

        await self.send(text_data=json.dumps({
            'content': content,
            'username': username
        }))

    async def get_shared_content(self):
        # Use aioredis to create a Redis client
        redis = await aioredis.from_url(REDIS_URL)
        content = await redis.get('shared_content')
        await redis.close()  # Close the Redis connection
        # Decode the bytes to a string, if content is not None
        send_content = content.decode('utf-8') if content is not None else ''
        return send_content


    async def save_shared_content(self, content):
        # Use aioredis to create a Redis client
        redis = await aioredis.from_url(REDIS_URL)
        await redis.set('shared_content', content)
        await redis.close()  # Close the Redis connection

    async def save_db(self, username):
        shared_content = await self.get_shared_content() 

        try:
            user = self.collection.find_one({ 'username': username })
            if not user:
                print("No mathcing user found")
                return

            update = {"$set": { "save_content": shared_content}}
            save_content = self.collection.update_one({ 'username': username }, update)

            print("save content is :", save_content)

            # Testing with shell
            if save_content.matched_count > 0:
                return {"success": True, "message": "Content saved successfully"}
            else:
                 return {"success": False, "message": "No matching document found"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
