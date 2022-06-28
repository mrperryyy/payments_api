import pytest
from api.app import app as application
from api.config import Config

@pytest.fixture()
def client():
    with application.test_client() as client:
        application.config.from_object(Config)
        yield client