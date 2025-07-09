from unittest.mock import MagicMock
from uuid import uuid4
import pytest
from app.schemas.schema_user import UserLogin
from app.schemas.token import Token
from app.exceptions import AuthorizationError
from app.services.services_auth import login_service

@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session with context manager support."""
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db


def test_service_auth_login_valid_credentials(mock_db_session, monkeypatch):
    """
    Unit test for login_service with valid email and password.
    """
    user_id = uuid4()
    user = MagicMock(id=user_id, email="test@example.com", hashed_password="hashed_pw")
    user_request = UserLogin(email="test@example.com", password="secret")

    def mock_find_user(db, email):
        return user

    def mock_verify_password(plain_password, hashed_password):
        return True

    def mock_create_access_token(data):
        return "mocked_token"

    monkeypatch.setattr("app.services.services_auth.find_user", mock_find_user)
    monkeypatch.setattr("app.services.services_auth.verify_password", mock_verify_password)
    monkeypatch.setattr("app.services.services_auth.create_access_token", mock_create_access_token)

    result = login_service(mock_db_session, user_request)

    assert isinstance(result, Token)
    assert result.access_token == "mocked_token"


def test_service_auth_login_invalid_password(mock_db_session, monkeypatch):
    """
    Unit test for login_service with invalid password.
    """
    user = MagicMock(email="test@example.com", hashed_password="hashed_pw")
    user_request = UserLogin(email="test@example.com", password="wrong")

    def mock_find_user(db, email):
        return user

    def mock_verify_password(plain_password, hashed_password):
        return False

    monkeypatch.setattr("app.services.services_auth.find_user", mock_find_user)
    monkeypatch.setattr("app.services.services_auth.verify_password", mock_verify_password)

    with pytest.raises(AuthorizationError):
        login_service(mock_db_session, user_request)


def test_service_auth_login_user_not_found(mock_db_session, monkeypatch):
    """
    Unit test for login_service when user is not found.
    """
    user_request = UserLogin(email="notfound@example.com", password="pw")

    def mock_find_user(db, email):
        return None

    monkeypatch.setattr("app.services.services_auth.find_user", mock_find_user)

    with pytest.raises(AuthorizationError):
        login_service(mock_db_session, user_request)