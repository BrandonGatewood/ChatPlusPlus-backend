import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime
from app.db.models.message import Message
from app.exceptions import AuthorizationError, ChatNotFoundError, NotFoundError
from app.schemas.schema_chat import ChatResponse
from app.services.services_chat import get_chat_service


@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session with context manager support."""
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db


def test_service_chat_get_chat(mock_db_session, monkeypatch):
    """
    Unit test for successful execution of get_chat_service.
    """
    user_id = uuid4()
    chat_id = uuid4()

    dummy_chat = MagicMock()

    # Patch chat_ownership with MagicMock returning True
    mock_chat_ownership = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", mock_chat_ownership)

    # Patch get_chat with MagicMock returning dummy_chat
    mock_get_chat = MagicMock(return_value=dummy_chat)
    monkeypatch.setattr("app.services.services_chat.get_chat", mock_get_chat)

    # Patch model_validate with MagicMock returning ChatResponse
    mock_model_validate = MagicMock(return_value=ChatResponse(
        id=chat_id, title="Test Chat", created_at=datetime.now(), messages=[]
    ))
    monkeypatch.setattr("app.schemas.schema_chat.ChatResponse.model_validate", mock_model_validate)

    result = get_chat_service(mock_db_session, chat_id, user_id)

    assert isinstance(result, ChatResponse)
    assert result.id == chat_id
    assert result.title == "Test Chat"

    mock_chat_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)
    mock_get_chat.assert_called_once_with(mock_db_session, chat_id)
    mock_model_validate.assert_called_once_with(dummy_chat)


def test_service_chat_get_chat_with_messages(mock_db_session, monkeypatch):
    """
    Unit test for successful execution of get_chat_service with messages.
    """
    user_id = uuid4()
    chat_id = uuid4()

    dummy_messages = [
        Message(
            id=uuid4(), chat_id=chat_id, sender="user", text="Hello", created_at=datetime.now()
        ),
        Message(
            id=uuid4(), chat_id=chat_id, sender="bot", text="Hi!", created_at=datetime.now()
        )
    ]

    dummy_chat = MagicMock()

    mock_chat_ownership = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", mock_chat_ownership)

    mock_get_chat = MagicMock(return_value=dummy_chat)
    monkeypatch.setattr("app.services.services_chat.get_chat", mock_get_chat)

    mock_model_validate = MagicMock(return_value=ChatResponse(
        id=chat_id, title="Chat with Messages", created_at=datetime.now(), messages=dummy_messages
    ))
    monkeypatch.setattr("app.schemas.schema_chat.ChatResponse.model_validate", mock_model_validate)

    result = get_chat_service(mock_db_session, chat_id, user_id)

    assert isinstance(result, ChatResponse)
    assert result.id == chat_id
    assert result.title == "Chat with Messages"
    assert len(result.messages) == 2
    assert result.messages[0].sender == "user"
    assert result.messages[1].sender == "bot"

    mock_chat_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)
    mock_get_chat.assert_called_once_with(mock_db_session, chat_id)
    mock_model_validate.assert_called_once_with(dummy_chat)


def test_service_chat_get_chat_unauthorized(mock_db_session, monkeypatch):
    """
    Unit test for get_chat_service when user is not authorized.
    """
    user_id = uuid4()
    chat_id = uuid4()

    mock_chat_ownership = MagicMock(return_value=False)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", mock_chat_ownership)

    with pytest.raises(AuthorizationError, match="Not Authorized"):
        get_chat_service(mock_db_session, chat_id, user_id)

    mock_chat_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)


def test_service_chat_get_chat_not_found(mock_db_session, monkeypatch):
    """
    Unit test for get_chat_service when chat is not found.
    """
    user_id = uuid4()
    chat_id = uuid4()

    mock_chat_ownership = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", mock_chat_ownership)

    mock_get_chat = MagicMock(side_effect=ChatNotFoundError("Chat does not exist"))
    monkeypatch.setattr("app.services.services_chat.get_chat", mock_get_chat)

    with pytest.raises(NotFoundError, match="Chat not found"):
        get_chat_service(mock_db_session, chat_id, user_id)

    mock_chat_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)
    mock_get_chat.assert_called_once_with(mock_db_session, chat_id)