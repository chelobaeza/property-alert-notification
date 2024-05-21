from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from property_alert_notification.adapters.event_processor import EventProcessor


@pytest.mark.asyncio
class TestEventProcessor:
    async def test_event_processor_calls_handler(self):
        handlers = [AsyncMock(), AsyncMock()]
        processor = EventProcessor(handlers=handlers)

        await processor.process(
            {"preferences": {}}
        )

        for handler in handlers:
            handler.can_handle.assert_called_once()
            handler.handle.assert_called_once()
            
    async def test_event_processor(self):
        cannot_handle = AsyncMock()
        cannot_handle.can_handle.return_value = False
        can_handle = AsyncMock()
        can_handle.can_handle.return_value = True
        handlers = [can_handle, cannot_handle]

        processor = EventProcessor(handlers=handlers)

        await processor.process(
            {"preferences": {}}
        )

        cannot_handle.handle.assert_not_called()
        can_handle.handle.assert_called_once()

