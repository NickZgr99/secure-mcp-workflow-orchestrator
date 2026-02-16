import asyncio
import logging
import sys
from apps.worker.app.events.consumer import consume_events

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

if __name__ == "__main__":
    try:
        asyncio.run(consume_events())
    except KeyboardInterrupt:
        pass
