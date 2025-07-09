from unittest.mock import MagicMock
import pytest
from app.schemas.token import Token
from app.services.services_auth import register_service
from app.schemas.schema_user import UserCreate
from app.exceptions import ValidationError


@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session with context manager support."""
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db


def test_service_auth_register_success(mock_db_session, monkeypatch):
    """
    Unit test for register_service with valid new email.
    """
    user_request = UserCreate(email="new@example.com", password="pass")

    def mock_check_email(db, email):
        return False

    def mock_create_user(db, email, password):
        return 42

    def mock_create_access_token(data):
        return "new_token"

    monkeypatch.setattr("app.services.services_auth.check_email", mock_check_email)
    monkeypatch.setattr("app.services.services_auth.create_user", mock_create_user)
    monkeypatch.setattr("app.services.services_auth.create_access_token", mock_create_access_token)

    result = register_service(mock_db_session, user_request)

    assert isinstance(result, Token)
    assert result.access_token == "new_token"


def test_service_auth_register_email_exists(mock_db_session, monkeypatch):
    """
    Unit test for register_service when email is already in use.
    """
    user_request = UserCreate(email="existing@example.com", password="pass")

    def mock_check_email(db, email):
        return True

    monkeypatch.setattr("app.services.services_auth.check_email", mock_check_email)

    with pytest.raises(ValidationError):
        register_service(mock_db_session, user_request)