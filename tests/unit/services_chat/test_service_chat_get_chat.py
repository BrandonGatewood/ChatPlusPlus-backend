from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4
import pytest

from app.db.models.message import Message
from app.exceptions import AuthorizationError, ChatNotFoundError, NotFoundError
from app.schemas.schema_chat import ChatResponse
from app.services.services_chat import get_chat_service


@pytest.fixture
def mock_db_session():
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db

def test_service_chat_get_chat(mock_db_session, monkeypatch):
    user_id = uuid4()
    chat_id = uuid4()

    # Dummy chat data (simulate DB model instance)
    dummy_chat = MagicMock()
    # Patch chat_ownership to return True (authorized)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", lambda db, c_id, u_id: True)
    # Patch get_chat to return dummy chat
    monkeypatch.setattr("app.services.services_chat.get_chat", lambda db, c_id: dummy_chat)
    # Patch ChatResponse.model_validate to return a ChatResponse instance (simulate Pydantic validation)
    monkeypatch.setattr("app.schemas.schema_chat.ChatResponse.model_validate", lambda chat: ChatResponse(id=chat_id, title="Test Chat", created_at=datetime.now(), messages=[]))

    result = get_chat_service(mock_db_session, chat_id, user_id)

    assert isinstance(result, ChatResponse)
    assert result.id == chat_id
    assert result.title == "Test Chat"

def test_service_chat_get_chat_with_messages(mock_db_session, monkeypatch):
    user_id = uuid4()
    chat_id = uuid4()

    dummy_messages = [
        Message(
            id=uuid4(),
            chat_id=chat_id,
            sender="user",
            text="Hello, this is a test message",
            created_at=datetime.now()
        ),
        Message(
            id=uuid4(),
            chat_id=chat_id,
            sender="bot",
            text="Hi, how can I help you?",
            created_at=datetime.now()
        )
    ]

    # Dummy chat data (simulate DB model instance)
    dummy_chat = MagicMock()
    # Patch chat_ownership to return True (authorized)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", lambda db, c_id, u_id: True)
    # Patch get_chat to return dummy chat
    monkeypatch.setattr("app.services.services_chat.get_chat", lambda db, c_id: dummy_chat)
    # Patch ChatResponse.model_validate to return a ChatResponse instance (simulate Pydantic validation)
    monkeypatch.setattr("app.schemas.schema_chat.ChatResponse.model_validate", lambda chat: ChatResponse(id=chat_id, title="Test Chat", created_at=datetime.now(), messages=dummy_messages))

    result = get_chat_service(mock_db_session, chat_id, user_id)

    assert isinstance(result, ChatResponse)
    assert result.id == chat_id
    assert result.title == "Test Chat"
    assert len(result.messages) == 2
    assert result.messages[0].sender == "user"
    assert result.messages[1].sender == "bot"

def test_service_chat_get_chat_unauthorized(mock_db_session, monkeypatch):
    user_id = uuid4()
    chat_id = uuid4()

    # Patch chat_ownership to return False (not authorized)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", lambda db, c_id, u_id: False)

    with pytest.raises(AuthorizationError, match="Not Authorized"):
        get_chat_service(mock_db_session, chat_id, user_id)

def test_service_chat_get_chat_not_found(mock_db_session, monkeypatch):
    user_id = uuid4()
    chat_id = uuid4()

    # Patch chat_ownership to return True (authorized)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", lambda db, c_id, u_id: True)
    # Patch get_chat to raise ChatNotFoundError
    def raise_chat_not_found(db, c_id):
        raise ChatNotFoundError("Chat does not exist")

    monkeypatch.setattr("app.services.services_chat.get_chat", raise_chat_not_found)

    with pytest.raises(NotFoundError, match="Chat not found"):
        get_chat_service(mock_db_session, chat_id, user_id)