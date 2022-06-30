import pytest
from api import app as application
from api.config import Config
from api.auth import basic_auth

@pytest.fixture()
def client(monkeypatch):
    with application.test_client() as client:
        application.config.from_object(Config)
        monkeypatch.setattr(basic_auth, 'authenticate', lambda x, y: True)
        yield client
