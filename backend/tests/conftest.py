"""
PocketBuzz Test Suite Configuration
Configures pytest for the entire test suite.
"""
import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_restaurant_id():
    """Fixture providing a test restaurant ID."""
    return "4c01898c-e005-4311-a6c7-f42c444022a9"


@pytest.fixture
def mock_campaign_data():
    """Fixture providing sample campaign data."""
    return {
        "id": "test-campaign-id",
        "restaurant_id": "4c01898c-e005-4311-a6c7-f42c444022a9",
        "strategy_type": "CUSTOM",
        "insight_text": "Wada Pav is trending!",
        "generated_caption": "Wada Pav 15% off today! 🌶️",
        "generated_image_url": "https://example.com/wadapav.jpg",
        "status": "PENDING",
        "target_audience": {"days": 30}
    }


@pytest.fixture
def mock_customer_phones():
    """Fixture providing test customer phone numbers."""
    return [
        "919766912776",
        "919730088010",
        "917276006234"
    ]


@pytest.fixture
def mock_menu():
    """Fixture providing sample menu data."""
    return {
        "Wada Pav": 50,
        "Misal Pav": 80,
        "Chicken Malvani": 350,
        "Tawa Fry Pomfret": 700,
        "Zunka": 200
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
