import logging

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from property_alert_notification.adapters.exceptions import QueueAdapterException
from property_alert_notification.adapters.queue import QueuePublisherBase
from property_alert_notification.models.notification import NotificationCreate
from property_alert_notification.models.preference import Preference
from property_alert_notification.services.exceptions import PreferencesNotFound, ServiceException

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, queue_adapter: QueuePublisherBase, db_session: AsyncSession) -> None:
        self.queue = queue_adapter
        self.db_session = db_session

    async def _get_user_preferences(self, user_id: int) -> Preference:
        # TODO: this can be moved to a better place
        query = select(Preference).where(Preference.user_id == user_id)
        return (await self.db_session.exec(query)).one_or_none()

    async def schedule(self, notification: NotificationCreate):
        try:
            preferences = await self._get_user_preferences(notification.user_id)
            if not preferences:
                raise PreferencesNotFound(f"Preferences not found for user_id: {notification.user_id}")
            
            # add preferences into queue message
            message = notification.model_dump()
            message.update({"preferences": preferences.model_dump()})

            await self.queue.enqueue(message)

        except QueueAdapterException as e:
            msg = f"QueueAdapter Error: {e}"
            logger.error(msg)
            raise ServiceException(msg) from e
