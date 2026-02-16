import asyncio
import json
import logging
from apps.api.app.cache.redis_client import get_redis
from apps.worker.app.executor import WorkflowExecutor
import os

logger = logging.getLogger(__name__)

EVENT_QUEUE_KEY = os.getenv("EVENT_QUEUE_KEY", "events:workflow")

async def consume_events():
    redis = await get_redis()
    logger.info(f"Worker started. Listening on {EVENT_QUEUE_KEY}...")
    
    while True:
        try:
            # BLPOP blocks until an item is available
            # Returns (key, element) tuple
            item = await redis.blpop(EVENT_QUEUE_KEY, timeout=5)
            
            if item:
                key, message_str = item
                message = json.loads(message_str)
                logger.info(f"Received event: {message}")
                
                if message.get("event") == "RunStarted":
                    run_id = message["payload"]["run_id"]
                    executor = WorkflowExecutor(run_id)
                    # Run execution in background task to not block consumer loop strictly? 
                    # For now, let's await it to keep it simple and safe (sequential processing per worker)
                    # Or create a task: asyncio.create_task(executor.execute())
                    await executor.execute()
                    
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
            await asyncio.sleep(1)

