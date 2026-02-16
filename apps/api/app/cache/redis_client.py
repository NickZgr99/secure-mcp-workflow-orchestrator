import redis.asyncio as redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        if not self.client:
            self.client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None

    async def get_client(self):
        if not self.client:
            await self.connect()
        return self.client

redis_client = RedisClient()

async def get_redis():
    client = await redis_client.get_client()
    return client
