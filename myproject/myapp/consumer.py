from channels.generic.websocket import AsyncWebsocketConsumer
import os
import redis.asyncio as aioredis
import json, pymongo

class EditorConsumer(AsyncWebsocketConsumer):
    # MongoDB setup
    DATABASE_URL = os.getenv('DATABASE_URL')
    db_name = os.getenv('db_name')
    db_collection = os.getenv('db_collection')

    # Redis URLs
    REDIS_INTERNAL_URL = os.getenv('REDIS_INTERNAL_URL')
    REDIS_EXTERNAL_URL = os.getenv('REDIS_EXTERNAL_URL')

    # Establish MongoDB connection
    client = pymongo.MongoClient(DATABASE_URL)
    db = client[db_name]
    collection = db[db_collection]

    async def connect(self):
        self.room_group_name = 'editor_group'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        shared_content = await self.get_shared_content(use_internal=True)
        await self.send(text_data=json.dumps({'content': shared_content}))

    async def get_shared_content(self, use_internal=True):
        # Choose Redis URL based on the context
        redis_url = self.REDIS_INTERNAL_URL if use_internal else self.REDIS_EXTERNAL_URL
        redis = await aioredis.from_url(redis_url)
        content = await redis.get('shared_content')
        await redis.close()
        return content.decode('utf-8') if content else ''

    async def save_shared_content(self, content, use_internal=True):
        redis_url = self.REDIS_INTERNAL_URL if use_internal else self.REDIS_EXTERNAL_URL
        redis = await aioredis.from_url(redis_url)
        await redis.set('shared_content', content)
        await redis.close()

    async def save_db(self, username):
        # Use external URL for saving to DB
        shared_content = await self.get_shared_content(use_internal=False)
        if not shared_content:
            return {"success": False, "message": "No content to save"}

        try:
            update = {"$set": {"content": shared_content}}
            result = self.collection.update_one({'username': username}, update)
            return {"success": True, "message": "Content saved successfully"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

# Additional methods as required for your application...

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
