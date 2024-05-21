import logging
from fastapi import APIRouter, status, HTTPException

from property_alert_notification.api.deps import NotificationServiceDep
from property_alert_notification.models.notification import NotificationCreate
from property_alert_notification.services.exceptions import PreferencesNotFound, ServiceException


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/")
async def schedule_notification(
    new_notification: NotificationCreate,
    service: NotificationServiceDep,
):
    try:

        await service.schedule(new_notification)

    except PreferencesNotFound as e:
        logger.error(f"Resource not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found for user")
    
    except ServiceException as e:
        msg = f"NotificationService error: {e}"
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=msg)

    return new_notification
