import abc
import asyncio
from contextlib import asynccontextmanager
import json
import logging
from typing import Coroutine
from aio_pika import DeliveryMode, Message, connect
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractIncomingMessage

from property_alert_notification.adapters.event_processor import EventProcessorBase

logger = logging.getLogger(__name__)


class QueuePublisherBase(abc.ABC):
    @abc.abstractmethod
    async def enqueue(self, notification: dict):
        pass


class QueueConsumerBase(abc.ABC):
    @abc.abstractmethod
    async def consume(self):
        pass


class RabbitMQConnector:
    def __init__(self, connection_url: str, routing_key: str) -> None:
        self.connection_url = connection_url
        self.routing_key = routing_key

    async def _connection(self) -> AbstractConnection:
        return await connect(self.connection_url)

    async def _create_channel(self, connection) -> AbstractChannel:
        return await connection.channel()

    @asynccontextmanager
    async def open_channel(self):
        connection = await self._connection()

        async with connection:
            channel = await self._create_channel(connection)

            yield channel


class RabbitMQPublisherAdapter(QueuePublisherBase):
    def __init__(self, connector: RabbitMQConnector) -> None:
        self.connector = connector

    def _create_message(self, notification: dict) -> Message:
        message = Message(
            bytes(json.dumps(notification), encoding="utf8"),
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        return message

    async def enqueue(self, notification: dict):
        async with self.connector.open_channel() as channel:
            message = self._create_message(notification)

            # Sending the message
            await channel.default_exchange.publish(
                message,
                routing_key=self.connector.routing_key,
            )
            logger.info("Message sended.")


class RabbitMQConsumerAdapter(QueueConsumerBase):
    def __init__(
        self,
        connector: RabbitMQConnector,
        on_message: Coroutine,
        prefetch_count: int = 1,
        durable_queue: bool = True,
    ) -> None:
        self.connector = connector
        self.on_message = on_message
        self.prefetch_count = prefetch_count
        self.durable_queue = durable_queue

    async def _declare_queue(self, channel: AbstractChannel):
        return await channel.declare_queue(
            self.connector.routing_key,
            durable=self.durable_queue,
        )

    async def consume(self) -> None:
        async with self.connector.open_channel() as channel:
            # Setting how many messages are dispatched to workers
            await channel.set_qos(prefetch_count=self.prefetch_count)

            # Declaring the queue
            queue = await self._declare_queue(channel)

            await queue.consume(self.on_message)
            await asyncio.Future()


class RabbitMQMessageProcessor:
    def __init__(self, processor: EventProcessorBase) -> None:
        self.processor = processor

    async def on_message(self, message: AbstractIncomingMessage) -> None:
        await asyncio.sleep(1)  # just for human eye testing

        async with message.process():
            str_message = message.body.decode()
            obj_message = json.loads(str_message)
            logger.info("message consumed")
            await self.processor.process(obj_message)
