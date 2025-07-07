from unittest.mock import MagicMock
from uuid import uuid4
import pytest
from app.exceptions import AuthorizationError, ChatNotFoundError, MessageNotFoundError, NotFoundError
from app.schemas.schema_message import EditMessageRequest, MessageRequest, MessageResponse
from app.services.services_message import edit_text_message_service


@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session with context manager support."""
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db


@pytest.fixture
def edit_message_request():
    """Fixture for a sample edit message request."""
    return EditMessageRequest(id=uuid4(), text="Hello bot")


def test_service_message_edit_message_success(mock_db_session, edit_message_request, monkeypatch):
    """
    Unit test for successful execution of edit_text_message_service.
    """
    user_id = uuid4()
    chat_id = uuid4()

    dummy_bot_response = MessageResponse(
        id=1, chat_id=chat_id, sender="bot", text="Bot responded."
    )

    # Patch dependencies with MagicMock so we can assert calls if needed
    mock_ownership = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.services_message.chat_ownership", mock_ownership)

    mock_edit_message = MagicMock()
    monkeypatch.setattr("app.services.services_message.edit_message", mock_edit_message)

    mock_build_prompt = MagicMock(return_value="Prompt text")
    monkeypatch.setattr("app.services.services_message.build_prompt", mock_build_prompt)

    mock_call_bot = MagicMock(return_value=dummy_bot_response)
    monkeypatch.setattr("app.services.services_message.call_bot", mock_call_bot)

    mock_add_message = MagicMock()
    monkeypatch.setattr("app.services.services_message.add_message", mock_add_message)

    result = edit_text_message_service(mock_db_session, chat_id, user_id, edit_message_request)

    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."

    # Optional: verify expected calls for extra confidence
    mock_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)
    mock_edit_message.assert_called_once_with(mock_db_session, edit_message_request.id, edit_message_request.text)
    mock_build_prompt.assert_called_once_with(mock_db_session, chat_id)
    mock_call_bot.assert_called_once_with("Prompt text")
    mock_add_message.assert_called_once_with(mock_db_session, chat_id, "bot", dummy_bot_response.text)


def test_service_message_edit_message_unauthorized(mock_db_session, edit_message_request, monkeypatch):
    """
    Unit test for edit_text_message_service when user is not authorized.
    """
    user_id = uuid4()
    chat_id = uuid4()

    mock_ownership = MagicMock(return_value=False)
    monkeypatch.setattr("app.services.services_message.chat_ownership", mock_ownership)

    with pytest.raises(AuthorizationError, match="Not Authorized"):
        edit_text_message_service(mock_db_session, chat_id, user_id, edit_message_request)

    mock_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)


def test_service_message_edit_message_not_found(mock_db_session, edit_message_request, monkeypatch):
    """
    Unit test for edit_text_message_service when message is not found.
    """
    user_id = uuid4()
    chat_id = uuid4()

    # Authorized access
    mock_ownership = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.services_message.chat_ownership", mock_ownership)

    # Simulate MessageNotFoundError on edit
    mock_edit_message = MagicMock(side_effect=MessageNotFoundError("Message does not exist"))
    monkeypatch.setattr("app.services.services_message.edit_message", mock_edit_message)

    with pytest.raises(NotFoundError, match="Message not found"):
        edit_text_message_service(mock_db_session, chat_id, user_id, edit_message_request)

    mock_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)
    mock_edit_message.assert_called_once_with(mock_db_session, edit_message_request.id, edit_message_request.text)