from channels.generic.websocket import AsyncWebsocketConsumer
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
import redis.asyncio as aioredis
import json, environ, pymongo

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
# env = environ.Env()
# env_file = BASE_DIR / ".env"
# environ.Env.read_env(env_file=env_file)

USE_EXTERNAL_REDIS = os.getenv('USE_EXTERNAL_REDIS', 'False') == 'True'
REDIS_URL = os.getenv('EXTERNAL_REDIS') if USE_EXTERNAL_REDIS else env('REDIS_URL')

class EditorConsumer(AsyncWebsocketConsumer):
    # Connect to MongoDB            
    DATABASE_URL = os.getenv('DATABASE_URL')
    db_name = os.getenv('db_name')
    db_collection = os.getenv('db_collection')

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
        await redis.close() 
        # Decode the bytes to a string, if content is not None
        send_content = content.decode('utf-8') if content is not None else ''
        return send_content


    async def save_shared_content(self, content):
        # Use aioredis to create a Redis client
        redis = await aioredis.from_url(REDIS_URL)
        await redis.set('shared_content', content)
        await redis.close()  


    async def save_db(self, username):
        shared_content = await self.get_shared_content() 

        try:
            user = self.collection.find_one({ 'username': username })
            if not user:
                print("No mathcing user found")
                return

            update = {"$set": { "content": shared_content}}
            result = self.collection.update_one({ 'username': username }, update)

        except Exception:
            return {"message": "Error while posting"}

    async def load_db(self, username):
        try:
            user = self.collection.find_one({ 'username': username })
            if not user:
                return {"success": False, "message": "No matching user found in DB"}

            content = user.get('content')
            print("Loaded content:", content)
            if not content:
                return {"success": False, "message": "No content available to store in Redis"}
            
            await self.save_shared_content(content)
            return {"success": True, "message": "Content successfully stored in Redis", "content": content}
        except Exception:
            return {"message": "Error while loading"}
