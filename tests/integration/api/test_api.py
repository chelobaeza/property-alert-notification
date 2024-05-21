from unittest.mock import AsyncMock, Mock

import pytest
from httpx import AsyncClient
from property_alert_notification.adapters.exceptions import QueueAdapterException
from property_alert_notification.api.deps import get_db, get_queue_adapter
from property_alert_notification.models.preference import Preference

from . import data as test_data

# engine = create_async_engine(str(settings.TEST_DATABASE_URL), connect_args={"check_same_thread": False})

# TestingSessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )


@pytest.mark.asyncio
class TestPreferences:
    @pytest.fixture()
    def mocked_session(self):
        mocked_session = AsyncMock()
        yield mocked_session

    @pytest.fixture
    def test_app(self, test_app, mocked_session):
        # mocking database dep
        test_app.dependency_overrides[get_db] = lambda: mocked_session
        yield test_app

    async def test_read_preference(self, test_client: AsyncClient, mocked_session):
        mocked_result = Mock()
        mocked_result.one_or_none.return_value = {
            "email_enabled": True,
            "sms_enabled": True,
        }
        mocked_session.exec.return_value = mocked_result

        response = await test_client.get("/preferences/1")

        assert response.status_code == 200
        assert response.json() == {"email_enabled": True, "sms_enabled": True}

    async def test_read_preference_not_found(
        self, test_client: AsyncClient, mocked_session
    ):
        mocked_result = Mock()
        mocked_result.one_or_none.return_value = None
        mocked_session.exec.return_value = mocked_result

        response = await test_client.get("/preferences/1")

        assert response.status_code == 404
        assert response.json() == {"detail": "Preference not found"}

    async def test_post_preference(self, test_client: AsyncClient, mocked_session):
        new_preference = {
            "email_enabled": True,
            "sms_enabled": False,
        }

        mocked_result = Mock()
        mocked_result.one_or_none.return_value = None
        mocked_session.exec.return_value = mocked_result

        response = await test_client.post("/preferences/1", json=new_preference)

        mocked_session.add.assert_called_once()
        mocked_session.commit.assert_called_once()
        assert response.status_code == 201
        assert response.json() == {"email_enabled": True, "sms_enabled": False}

    async def test_post_preference_already_exist_error(
        self, test_client: AsyncClient, mocked_session
    ):
        new_preference = {
            "email_enabled": True,
            "sms_enabled": False,
        }

        mocked_result = Mock()
        mocked_result.one_or_none.return_value = Preference(
            **{"email_enabled": True, "sms_enabled": True}
        )
        mocked_session.exec.return_value = mocked_result

        response = await test_client.post("/preferences/1", json=new_preference)

        mocked_session.add.assert_not_called()
        mocked_session.commit.assert_not_called()
        assert response.status_code == 400
        assert response.json() == {"detail": "Preferences already exist for user_id=1"}

    @pytest.mark.parametrize(
        "data", test_data.test_post_reference_validation_error_data
    )
    async def test_post_preference_validation_error(
        self, data, test_client: AsyncClient
    ):
        response = await test_client.post("/preferences/1", json=data["new_preference"])

        assert response.status_code == 422
        assert response.json() == data["expected_error"]


@pytest.mark.asyncio
class TestNotifications:
    @pytest.fixture
    def mocked_queue_adapter(self):
        mocked_queue = AsyncMock()
        yield mocked_queue

    @pytest.fixture
    def mocked_session(self):
        mocked_session = AsyncMock()
        mocked_result = Mock()
        mocked_result.one_or_none.return_value = Preference(
            **{
                "email_enabled": True,
                "sms_enabled": True,
            }
        )
        mocked_session.exec.return_value = mocked_result
        yield mocked_session

    @pytest.fixture
    def test_app(self, test_app, mocked_queue_adapter, mocked_session):
        # mocking queue dep
        test_app.dependency_overrides[get_queue_adapter] = lambda: mocked_queue_adapter
        test_app.dependency_overrides[get_db] = lambda: mocked_session
        yield test_app

    async def test_schedule_notification(
        self, test_client: AsyncClient, mocked_queue_adapter
    ):
        new_notification = {
            "title": "Notification title",
            "message": "Notification message",
            "user_id": 1234,
            "user_email": "user@test.com",
            "user_phone_number": "123123123",
        }

        response = await test_client.post("/notifications/", json=new_notification)

        mocked_queue_adapter.enqueue.assert_called_once()
        assert response.status_code == 200
        assert response.json() == new_notification

    @pytest.mark.parametrize("data", test_data.test_post_notification_validation_error)
    async def test_post_notification_validation_error(
        self, data, test_client: AsyncClient
    ):
        response = await test_client.post(
            "/notifications/", json=data["new_notification"]
        )

        assert response.status_code == 422
        # assert response.json() == data["expected_error"]

    async def test_post_notification_exception(
        self, test_client: AsyncClient, mocked_queue_adapter
    ):
        new_notification = {
            "title": "Notification title",
            "message": "Notification message",
            "user_id": 1234,
            "user_email": "user@test.com",
            "user_phone_number": "123123123",
        }

        mocked_queue_adapter.enqueue.side_effect = QueueAdapterException

        response = await test_client.post("/notifications/", json=new_notification)

        assert response.status_code == 503
