from unittest.mock import MagicMock
from uuid import uuid4
import pytest
from app.exceptions import AuthorizationError, ChatNotFoundError, NotFoundError
from app.schemas.schema_message import MessageRequest, MessageResponse
from app.services.services_message import add_message_service


@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session with context manager support."""
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db


@pytest.fixture
def message_request():
    """MessageRequest with no attached files."""
    return MessageRequest(text="Hello test message", files=[])


def test_service_message_add_message(mock_db_session, message_request, monkeypatch):
    """
    Unit test for successful execution of add_message_service.
    """
    # Arrange: generate a to simulate a real data 
    user_id = uuid4()
    chat_id = uuid4()
    dummy_bot_response = MessageResponse(
        id=1, chat_id=chat_id, sender="bot", text="Bot responded."
    )

    # Arrange: patch dependencies with MagicMock so we can assert calls
    mock_chat_ownership = MagicMock(return_value=True)
    mock_save_user_messages = MagicMock()
    mock_build_prompt = MagicMock(return_value="Prompt text")
    mock_call_bot = MagicMock(return_value=dummy_bot_response)
    mock_add_message = MagicMock()

    monkeypatch.setattr("app.services.services_message.chat_ownership", mock_chat_ownership)
    monkeypatch.setattr("app.services.services_message.save_user_messages", mock_save_user_messages)
    monkeypatch.setattr("app.services.services_message.build_prompt", mock_build_prompt)
    monkeypatch.setattr("app.services.services_message.call_bot", mock_call_bot)
    monkeypatch.setattr("app.services.services_message.add_message", mock_add_message)

    # Act
    result = add_message_service(mock_db_session, chat_id, user_id, message_request)

    # Assert: output correctness
    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."

    # Assert: all expected calls happened once with expected args
    mock_chat_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)
    mock_save_user_messages.assert_called_once_with(mock_db_session, chat_id, message_request)
    mock_build_prompt.assert_called_once_with(mock_db_session, chat_id)
    mock_call_bot.assert_called_once_with("Prompt text")
    mock_add_message.assert_called_once_with(mock_db_session, chat_id, "bot", dummy_bot_response.text) 


def test_service_message_add_message_unauthorized(mock_db_session, message_request, monkeypatch):
    """
    Unit test for add_message_service: if chat_ownership returns False,
    the service should raise NotFoundError.
    """
    # Arrange: generate to simulate a real data 
    user_id = uuid4()
    chat_id = uuid4()

    # Arrange: patch chat_ownership with MagicMock returning False
    mock_chat_ownership = MagicMock(return_value=False)
    monkeypatch.setattr("app.services.services_message.chat_ownership", mock_chat_ownership)

    # Act + Assert: service should raise AuthorizationError
    with pytest.raises(AuthorizationError, match="Not Authorized"):
        add_message_service(mock_db_session, chat_id, user_id, message_request)

    # Assert: ensure chat_ownership was called once with expected arguments
    mock_chat_ownership.assert_called_once_with(mock_db_session, chat_id, user_id) 


def test_service_message_add_message_chat_not_found(mock_db_session, message_request, monkeypatch):
    """
    Unit test for add_message_service: if add_message raises ChatNotFoundError,
    the service should raise NotFoundError after completing previous steps. 
    """
    # Arrange: generate to simulate a real data 
    user_id = uuid4()
    chat_id = uuid4()

    # Arrange: patch chat_ownership with MagicMock returning False
    mock_chat_ownership = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.services_message.chat_ownership", mock_chat_ownership) 

    # Arrange: patch save_user_messages to raise ChatNotFoundError
    mock_save_user_messages = MagicMock(side_effect=ChatNotFoundError("Chat does not exist"))
    monkeypatch.setattr("app.services.services_message.save_user_messages", mock_save_user_messages)

    # Act + Assert: verify NotFoundError is raised with the expected message
    with pytest.raises(NotFoundError, match="Chat not found"):
        add_message_service(mock_db_session, chat_id, user_id, message_request)

    # Extra Assert: confirm create_chat was actually called once with expected args
    mock_save_user_messages.assert_called_once_with(mock_db_session, chat_id, message_request)  