import logging

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from property_alert_notification.models.preference import Preference
from property_alert_notification.services.exceptions import PreferencesAlreadyExist

logger = logging.getLogger(__name__)


class PreferenceService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get(self, user_id: int) -> Preference:
        query = select(Preference).where(Preference.user_id == user_id)
        preference = (await self.db_session.exec(query)).one_or_none()
        return preference

    async def create(self, preference: Preference) -> Preference:
        preference_exists = await self.get(preference.user_id)
        if preference_exists:
            raise PreferencesAlreadyExist(f"Preferences already exist for user_id={preference.user_id}")
        self.db_session.add(preference)
        await self.db_session.commit()
        await self.db_session.refresh(preference)
        return preference
