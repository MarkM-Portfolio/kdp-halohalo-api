from app import create_app
import pytest


@pytest.fixture
def client():
    flask_app = create_app("TEST")

    with flask_app.test_client() as client:
        yield client
