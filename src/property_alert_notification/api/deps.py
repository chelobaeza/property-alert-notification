from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from property_alert_notification.core.config import settings
from property_alert_notification.core.db import SessionLocal
from property_alert_notification.services.notification import NotificationService
from property_alert_notification.adapters.queue import QueuePublisherBase, RabbitMQPublisherAdapter, RabbitMQConnector
from property_alert_notification.services.preference import PreferenceService


async def get_db() -> AsyncGenerator[AsyncSession, None, None]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]

async def get_queue_adapter():
    connector = RabbitMQConnector(connection_url=settings.QUEUE_BROKER_URL, routing_key=settings.QUEUE_ROUTING_KEY)
    queue = RabbitMQPublisherAdapter(connector=connector)
    yield queue

QueueDep = Annotated[QueuePublisherBase, Depends(get_queue_adapter)]


async def get_notification_service(queue_adapter: QueueDep, db_session: SessionDep):
    yield NotificationService(queue_adapter=queue_adapter, db_session=db_session)


NotificationServiceDep = Annotated[
    NotificationService, Depends(get_notification_service)
]

async def get_preference_service(db_session: SessionDep):
    yield PreferenceService(db_session=db_session)

PreferenceServiceDep = Annotated[
    PreferenceService, Depends(get_preference_service)
]
