import json
import os
from ..cache.redis_client import get_redis

EVENT_QUEUE_KEY = os.getenv("EVENT_QUEUE_KEY", "events:workflow")

class EventBus:
    async def publish(self, event_name: str, payload: dict):
        redis = await get_redis()
        message = {
            "event": event_name,
            "payload": payload
        }
        await redis.rpush(EVENT_QUEUE_KEY, json.dumps(message))

event_bus = EventBus()
