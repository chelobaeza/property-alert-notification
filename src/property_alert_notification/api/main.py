from fastapi import APIRouter

from property_alert_notification.api.routes import notifications, preferences


api_router = APIRouter()
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])