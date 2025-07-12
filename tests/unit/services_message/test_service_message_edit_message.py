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
def edited_message_request():
    """Fixture for a sample edit message request."""
    return EditMessageRequest(text="Hello bot")


def test_service_message_edit_message_success(mock_db_session, edited_message_request, monkeypatch):
    """
    Unit test for successful execution of edit_text_message_service.
    """
    user_id = uuid4()
    chat_id = uuid4()
    message_id = uuid4()

     # Patch chat ownership to True
    mock_ownership = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.services_message.chat_ownership", mock_ownership)

    # Patch edit_message function
    mock_edit_message = MagicMock()
    monkeypatch.setattr("app.services.services_message.edit_message", mock_edit_message)

    # Call service
    result = edit_text_message_service(
        mock_db_session, user_id, chat_id, message_id, edited_message_request
    )

    # Service returns None
    assert result is None

    # Verify expected calls
    mock_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)
    mock_edit_message.assert_called_once_with(mock_db_session, message_id, edited_message_request.text)


def test_service_message_edit_message_unauthorized(mock_db_session, edited_message_request, monkeypatch):
    """
    Unit test for edit_text_message_service when user is not authorized.
    """
    user_id = uuid4()
    chat_id = uuid4()
    message_id = uuid4()

    mock_ownership = MagicMock(return_value=False)
    monkeypatch.setattr("app.services.services_message.chat_ownership", mock_ownership)

    with pytest.raises(AuthorizationError, match="Not Authorized"):
        edit_text_message_service(mock_db_session, user_id, chat_id, message_id, edited_message_request)

    mock_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)


def test_service_message_edit_message_not_found(mock_db_session, edited_message_request, monkeypatch):
    """
    Unit test for edit_text_message_service when message is not found.
    """
    user_id = uuid4()
    chat_id = uuid4()
    message_id = uuid4()

    # Authorized access
    mock_ownership = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.services_message.chat_ownership", mock_ownership)

    # Simulate MessageNotFoundError on edit
    mock_edit_message = MagicMock(side_effect=MessageNotFoundError("Message does not exist"))
    monkeypatch.setattr("app.services.services_message.edit_message", mock_edit_message)

    with pytest.raises(NotFoundError, match="Message not found"):
        edit_text_message_service(mock_db_session, user_id, chat_id, message_id, edited_message_request)

    mock_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)
    mock_edit_message.assert_called_once_with(mock_db_session, message_id, edited_message_request.text)