import abc
import logging
from typing import List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EventProcessorBase(abc.ABC):
    @abc.abstractmethod
    async def process(self, event: dict):
        pass


class EventHandlerBase(abc.ABC):
    @abc.abstractmethod
    async def handle(self, event: dict):
        pass

    @abc.abstractmethod
    async def can_handle(self, preferences: dict) -> bool:
        pass


class EventProcessor:
    def __init__(self, handlers: List[EventHandlerBase]) -> None:
        self.handlers = handlers

    async def process(self, event: dict):
        preferences = event["preferences"]

        # only handlers that can handle it ;)
        handlers = [
            handler
            for handler in self.handlers
            if await handler.can_handle(preferences)
        ]

        for handler in handlers:
            await handler.handle(event=event)


class EmailHandler(EventHandlerBase):
    async def can_handle(self, preferences: dict) -> bool:
        return preferences["email_enabled"]

    async def handle(self, event: dict):
        email = event["user_email"]
        print(f"Email Hander executed with {email}")


class SMSHandler(EventHandlerBase):
    async def can_handle(self, preferences: dict) -> bool:
        return preferences["sms_enabled"]

    async def handle(self, event: dict):
        phone = event["user_phone_number"]
        print(f"SMS Hander executed with {phone}")
