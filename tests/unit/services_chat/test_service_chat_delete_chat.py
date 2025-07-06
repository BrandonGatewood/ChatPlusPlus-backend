import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from app.exceptions import AuthorizationError, ChatNotFoundError, NotFoundError
from app.services.services_chat import delete_chat_service

@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session with context manager support."""
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db

def test_service_chat_delete_chat(mock_db_session, monkeypatch):
    """
    Successful deletion of chat.
    """
    user_id = uuid4()
    chat_id = uuid4()

    # Patch chat_ownership to return True (user owns chat)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", lambda db, c_id, u_id: True)
    # Patch delete_chat to do nothing (simulate successful deletion)
    monkeypatch.setattr("app.services.services_chat.delete_chat", lambda db, c_id: None)

    # Should not raise
    delete_chat_service(mock_db_session, chat_id, user_id)

def test_service_chat_delete_chat_unauthorized(mock_db_session, monkeypatch):
    user_id = uuid4()
    chat_id = uuid4()

    # Patch chat_ownership to return False (user does not own chat)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", lambda db, c_id, u_id: False)

    with pytest.raises(AuthorizationError, match="Not Authorized"):
        delete_chat_service(mock_db_session, chat_id, user_id)

def test_service_chat_delete_chat_raise_chat_not_found(mock_db_session, monkeypatch):
    user_id = uuid4()
    chat_id = uuid4()

    # Patch chat_ownership to return True (authorized)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", lambda db, c_id, u_id: True)
    # Patch delete_chat to raise ChatNotFoundError
    def raise_chat_not_found(db, c_id):
        raise ChatNotFoundError("Chat does not exist")

    monkeypatch.setattr("app.services.services_chat.delete_chat", raise_chat_not_found)

    with pytest.raises(NotFoundError, match="Chat not found"):
        delete_chat_service(mock_db_session, chat_id, user_id)