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
    Unit test for successful execution of delete_chat_service.
    """
    # Arrange: generate to simulate a real data 
    user_id = uuid4()
    chat_id = uuid4()

    # Patch chat_ownership with MagicMock returning True (user owns chat)
    mock_chat_ownership = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", mock_chat_ownership)

    # Patch delete_chat with MagicMock that simulates successful deletion (returns None)
    mock_delete_chat = MagicMock(return_value=None)
    monkeypatch.setattr("app.services.services_chat.delete_chat", mock_delete_chat)

    # Act: call the service (should not raise any exceptions)
    delete_chat_service(mock_db_session, chat_id, user_id)

    # Assert: check chat_ownership was called once with expected args
    mock_chat_ownership.assert_called_once_with(mock_db_session, chat_id, user_id)
    # Assert: check delete_chat was called once with expected args
    mock_delete_chat.assert_called_once_with(mock_db_session, chat_id) 


def test_service_chat_delete_chat_unauthorized(mock_db_session, monkeypatch):
    """
    Unit test for delete_chat_service when user is not authorized.
    """
    # Arrange: generate to simulate a real data 
    user_id = uuid4()
    chat_id = uuid4()

    # Arrange: patch chat_ownership with MagicMock returning False
    mock_chat_ownership = MagicMock(return_value=False)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", mock_chat_ownership)

    with pytest.raises(AuthorizationError, match="Not Authorized"):
        delete_chat_service(mock_db_session, chat_id, user_id)

    # Assert: ensure chat_ownership was called once with expected arguments
    mock_chat_ownership.assert_called_once_with(mock_db_session, chat_id, user_id) 


def test_service_chat_delete_chat_raise_chat_not_found(mock_db_session, monkeypatch):
    """
    Unit test for delete_chat_service when chat is not found.
    """
    # Arrange: generate to simulate a real data 
    user_id = uuid4()
    chat_id = uuid4()

    # Arrange: patch chat_ownership with MagicMock returning False
    mock_chat_ownership = MagicMock(return_value=True)
    monkeypatch.setattr("app.services.services_chat.chat_ownership", mock_chat_ownership) 

    # Arrange: patch save_user_messages to raise ChatNotFoundError
    mock_delete_chat = MagicMock(side_effect=ChatNotFoundError("Chat does not exist"))
    monkeypatch.setattr("app.services.services_chat.delete_chat", mock_delete_chat)

    # Act + Assert: verify NotFoundError is raised with the expected message
    with pytest.raises(NotFoundError, match="Chat not found"):
        delete_chat_service(mock_db_session, chat_id, user_id)
    
    # Assert
    mock_delete_chat.assert_called_once_with(mock_db_session, chat_id)