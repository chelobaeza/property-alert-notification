from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from property_alert_notification.adapters.exceptions import QueueAdapterException
from property_alert_notification.models.notification import NotificationCreate
from property_alert_notification.models.preference import Preference
from property_alert_notification.services.exceptions import ServiceException
from property_alert_notification.services.notification import NotificationService


@pytest.mark.asyncio
class TestNotificationService:
    @pytest_asyncio.fixture
    async def mocked_session(self):
        mocked_session = AsyncMock()
        mocked_result = Mock()
        mocked_result.one_or_none.return_value = Preference(**{
            "email_enabled": True,
            "sms_enabled": True,
        })
        mocked_session.exec.return_value = mocked_result
        yield mocked_session

    async def test_schedule_notification(self, mocked_session):
        mocked_queue = AsyncMock()
        service = NotificationService(queue_adapter=mocked_queue, db_session=mocked_session)
        notification = NotificationCreate(
            title="title",
            message="message",
            user_id=123123,
            user_email= "user@test.com",
            user_phone_number= "123123123"
        )
        
        await service.schedule(notification=notification)

        mocked_queue.enqueue.assert_called_once()
        
    async def test_schedule_notification_exception(self, mocked_session):
        mocked_queue = AsyncMock()
        mocked_queue.enqueue.side_effect = QueueAdapterException
        service = NotificationService(queue_adapter=mocked_queue, db_session=mocked_session)
        notification = NotificationCreate(
            title="title",
            message="message",
            user_id=123123,
            user_email= "user@test.com",
            user_phone_number= "123123123"
        )
        
        with pytest.raises(ServiceException):
            await service.schedule(notification=notification)

        mocked_queue.enqueue.assert_called_once()