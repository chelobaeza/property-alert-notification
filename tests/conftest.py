
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from property_alert_notification.core.config import settings
from property_alert_notification.main import app




@pytest.fixture
def test_app():
    """Used to override fastapi dependencies
    i.e:
        @pytest.fixture
        def test_app(self, test_app, new_dependency):
            # mocking queue dep
            test_app.dependency_overrides[get_queue_adapter] = lambda: new_dependency
            yield test_app
        
        pay attention to the upper call to the global fixture test_app
    """
    yield app


@pytest_asyncio.fixture
async def test_client(test_app):
    base_url = "http://test.local" + settings.API_V1_STR
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url=base_url
    ) as client:
        yield client