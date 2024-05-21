import asyncio
import json
import logging

from property_alert_notification.adapters.event_processor import (
    EmailHandler,
    EventProcessor,
    SMSHandler,
)
from property_alert_notification.adapters.queue import (
    RabbitMQConnector,
    RabbitMQConsumerAdapter,
    RabbitMQMessageProcessor,
)
from property_alert_notification.core.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def consume() -> None:
    print("Consumer started.")

    processor = EventProcessor(handlers=[EmailHandler(), SMSHandler()])
    msg_processor = RabbitMQMessageProcessor(processor=processor)

    connector = RabbitMQConnector(
        connection_url=settings.QUEUE_BROKER_URL, routing_key=settings.QUEUE_ROUTING_KEY
    )
    queue = RabbitMQConsumerAdapter(
        connector=connector, on_message=msg_processor.on_message
    )
    await queue.consume()


if __name__ == "__main__":
    asyncio.run(consume())
