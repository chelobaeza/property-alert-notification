import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from property_alert_notification import initial_data
from property_alert_notification.api.main import api_router
from property_alert_notification.core.config import settings
from property_alert_notification.notification_worker import worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == "local":
        # initialize database
        await initial_data.init()

        # initialize notification worker with the app
        # the worker can be run in a separate standalone process by running the worker.py file
        _ = asyncio.create_task(worker.consume())
    
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(api_router, prefix=settings.API_V1_STR)
