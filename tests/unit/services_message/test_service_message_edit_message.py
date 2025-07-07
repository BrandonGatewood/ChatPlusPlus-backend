from unittest.mock import MagicMock
from uuid import uuid4
import pytest
from app.exceptions import AuthorizationError, ChatNotFoundError, MessageNotFoundError, NotFoundError
from app.schemas.schema_message import EditMessageRequest, MessageRequest, MessageResponse
from app.services.services_message import add_message_service, edit_text_message_service

@pytest.fixture
def mock_db_session():
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db

@pytest.fixture
def message_request():
    return MessageRequest(text="Hello test message", files=[])

@pytest.fixture
def edit_message_request():
    return EditMessageRequest(id=uuid4(), text="Hello bot")

def test_service_message_edit_message(mock_db_session, edit_message_request, monkeypatch):
    """
    Unit test for successful execution of edit_message_service.
    """
    user_id = uuid4()
    chat_id = uuid4()

    dummy_bot_response = MessageResponse(
        id=1, chat_id=chat_id, sender="bot", text="Bot responded."
    )

    # Arrange: patch dependencies
    monkeypatch.setattr("app.services.services_message.chat_ownership", lambda db, chat_id, user_id: True)
    monkeypatch.setattr("app.services.services_message.edit_message", lambda db, message_id, msg: None)
    monkeypatch.setattr("app.services.services_message.build_prompt", lambda db, chat_id: "Prompt text")
    monkeypatch.setattr("app.services.services_message.call_bot", lambda prompt: dummy_bot_response)
    monkeypatch.setattr("app.services.services_message.add_message", lambda db, chat_id, sender, text: None)

    result = edit_text_message_service(mock_db_session, chat_id, user_id, edit_message_request)

    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded." 

def test_service_message_edit_text_message_unauthorized(mock_db_session, edit_message_request, monkeypatch):
    """
    Unit test for edit_text_message_service when user is not authorized.
    """
    user_id = uuid4()
    chat_id = uuid4()

    # Arrange: patch dependencies
    monkeypatch.setattr("app.services.services_message.chat_ownership", lambda db, chat_id, user_id: False)

    with pytest.raises(AuthorizationError, match="Not Authorized"):
        edit_text_message_service(
            mock_db_session,
            chat_id,
            user_id,
            edit_message_request
        )

def test_service_message_edit_text_message_not_found(mock_db_session, edit_message_request, monkeypatch):
    """
    Unit test for edit_text_message_service when message is not found.
    """
    user_id = uuid4()
    chat_id = uuid4()

    # Arrange: patch dependencies
    monkeypatch.setattr("app.services.services_message.chat_ownership", lambda db, chat_id, user_id: True)

    # Patch edit_text_message_service to raise MessageNotFoundError when called
    def raise_message_not_found(db, m_id, msg):
        raise MessageNotFoundError("Message does not exist")

    monkeypatch.setattr("app.services.services_message.edit_message", raise_message_not_found)

    # Act + Assert: service should raise NotFoundError
    with pytest.raises(NotFoundError, match="Message not found"):
        edit_text_message_service(mock_db_session, chat_id, user_id, edit_message_request)