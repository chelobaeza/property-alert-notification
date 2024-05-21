import logging
from fastapi import APIRouter, HTTPException, status

from property_alert_notification.api.deps import PreferenceServiceDep
from property_alert_notification.models.preference import (
    Preference,
    PreferenceCreate,
    PreferencePublic,
)
from property_alert_notification.services.exceptions import PreferencesAlreadyExist

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{user_id}", response_model=PreferencePublic)
async def read_preference(user_id: int, service: PreferenceServiceDep):
    preference = await service.get(user_id=user_id)
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    return preference


@router.post(
    "/{user_id}", response_model=PreferencePublic, status_code=status.HTTP_201_CREATED
)
async def create_preference(
    user_id: int, new_preference: PreferenceCreate, service: PreferenceServiceDep
):
    preference = Preference.model_validate(new_preference, update={"user_id": user_id})
    try:
        return await service.create(preference)
    except PreferencesAlreadyExist:
        msg = f"Preferences already exist for {user_id=}"
        logger.warning(msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
