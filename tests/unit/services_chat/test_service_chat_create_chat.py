import pytest
from uuid import uuid4
from io import BytesIO
from unittest.mock import MagicMock
from fastapi import UploadFile
from app.exceptions import ChatNotFoundError, NotFoundError, UserNotFoundError
from app.schemas.schema_message import MessageRequest, MessageResponse
from app.services.services_chat import create_chat_service


@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session with context manager support."""
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db


### Fixtures for different request payloads
@pytest.fixture
def message_request_empty_files():
    """MessageRequest with no attached files."""
    return MessageRequest(
        text="Hello, this is a test message.",
        files=[]
    )


@pytest.fixture
def message_request_one_pdf_file():
    """MessageRequest with a single PDF file."""
    return MessageRequest(
        text="Hello, this is a test message.",
        files=[
            UploadFile(
                filename="dummy.pdf",
                file=BytesIO(b"dummy content")
            )
        ]
    )


@pytest.fixture
def message_request_one_docx_file():
    """MessageRequest with a single DOCX file."""
    return MessageRequest(
        text="Hello, this is a test message.",
        files=[
            UploadFile(
                filename="dummy.docx",
                file=BytesIO(b"dummy content")
            )
        ]
    )


@pytest.fixture
def message_request_multiple_files():
    """MessageRequest with multiple PDF and DOCX files."""
    return MessageRequest(
        text="Hello, this is a test message.",
        files=[
            UploadFile(filename="dummy1.pdf", file=BytesIO(b"dummy content")),
            UploadFile(filename="dummy2.pdf", file=BytesIO(b"dummy content")),
            UploadFile(filename="dummy.docx", file=BytesIO(b"dummy content"))
        ]
    )


def patch_create_chat_dependencies(monkeypatch, dummy_chat, dummy_bot_response):
    """
    Helper: patch all functions called by create_chat_service using MagicMock,
    so they can be asserted later if needed.
    """
    mock_create_chat = MagicMock(return_value=dummy_chat)
    mock_save_user_messages = MagicMock()
    mock_build_prompt = MagicMock(return_value="Prompt for bot")
    mock_call_bot = MagicMock(return_value=dummy_bot_response)
    mock_add_message = MagicMock()

    monkeypatch.setattr("app.services.services_chat.create_chat", mock_create_chat)
    monkeypatch.setattr("app.services.services_chat.save_user_messages", mock_save_user_messages)
    monkeypatch.setattr("app.services.services_chat.build_prompt", mock_build_prompt)
    monkeypatch.setattr("app.services.services_chat.call_bot", mock_call_bot)
    monkeypatch.setattr("app.services.services_chat.add_message", mock_add_message)

    return (
        mock_create_chat,
        mock_save_user_messages,
        mock_build_prompt,
        mock_call_bot,
        mock_add_message,
    )


def test_service_chat_create_chat_empty_files(mock_db_session, message_request_empty_files, monkeypatch):
    """
    Unit test for create_chat_service with user text and no files.
    """
    user_id = uuid4()
    dummy_chat = MagicMock(id=1)
    dummy_bot_response = MessageResponse(id=1, chat_id=1, sender="bot", text="Bot responded.")

    # Arrange
    mocks = patch_create_chat_dependencies(monkeypatch, dummy_chat, dummy_bot_response)

    # Act
    result = create_chat_service(mock_db_session, user_id, message_request_empty_files)

    # Assert: result correctness
    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."

    # Assert: verify calls
    (mock_create_chat, mock_save_user_messages, mock_build_prompt, mock_call_bot, mock_add_message) = mocks
    mock_create_chat.assert_called_once_with(mock_db_session, user_id, "Chat Title")
    mock_save_user_messages.assert_called_once_with(mock_db_session, dummy_chat.id, message_request_empty_files)
    mock_build_prompt.assert_called_once_with(mock_db_session, dummy_chat.id)
    mock_call_bot.assert_called_once_with("Prompt for bot")
    mock_add_message.assert_called_once_with(mock_db_session, dummy_chat.id, "bot", dummy_bot_response.text)


def test_service_chat_create_chat_one_pdf_file(mock_db_session, message_request_one_pdf_file, monkeypatch):
    """
    Unit test for create_chat_service with user text and one PDF file.
    """
    user_id = uuid4()
    dummy_chat = MagicMock(id=1)
    dummy_bot_response = MessageResponse(id=1, chat_id=1, sender="bot", text="Bot responded.")

    mocks = patch_create_chat_dependencies(monkeypatch, dummy_chat, dummy_bot_response)

    result = create_chat_service(mock_db_session, user_id, message_request_one_pdf_file)

    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."

    (mock_create_chat, mock_save_user_messages, mock_build_prompt, mock_call_bot, mock_add_message) = mocks
    mock_create_chat.assert_called_once_with(mock_db_session, user_id, "Chat Title")
    mock_save_user_messages.assert_called_once_with(mock_db_session, dummy_chat.id, message_request_one_pdf_file)
    mock_build_prompt.assert_called_once_with(mock_db_session, dummy_chat.id)
    mock_call_bot.assert_called_once_with("Prompt for bot")
    mock_add_message.assert_called_once_with(mock_db_session, dummy_chat.id, "bot", dummy_bot_response.text)


def test_service_chat_create_chat_one_docx_file(mock_db_session, message_request_one_docx_file, monkeypatch):
    """
    Unit test for create_chat_service with user text and one DOCX file.
    """
    user_id = uuid4()
    dummy_chat = MagicMock(id=1)
    dummy_bot_response = MessageResponse(id=1, chat_id=1, sender="bot", text="Bot responded.")

    mocks = patch_create_chat_dependencies(monkeypatch, dummy_chat, dummy_bot_response)

    result = create_chat_service(mock_db_session, user_id, message_request_one_docx_file)

    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."

    (mock_create_chat, mock_save_user_messages, mock_build_prompt, mock_call_bot, mock_add_message) = mocks
    mock_create_chat.assert_called_once_with(mock_db_session, user_id, "Chat Title")
    mock_save_user_messages.assert_called_once_with(mock_db_session, dummy_chat.id, message_request_one_docx_file)
    mock_build_prompt.assert_called_once_with(mock_db_session, dummy_chat.id)
    mock_call_bot.assert_called_once_with("Prompt for bot")
    mock_add_message.assert_called_once_with(mock_db_session, dummy_chat.id, "bot", dummy_bot_response.text)


def test_service_chat_create_chat_multiple_files(mock_db_session, message_request_multiple_files, monkeypatch):
    """
    Unit test for create_chat_service with user text and multiple PDF/DOCX files.
    """
    user_id = uuid4()
    dummy_chat = MagicMock(id=1)
    dummy_bot_response = MessageResponse(id=1, chat_id=1, sender="bot", text="Bot responded.")

    mocks = patch_create_chat_dependencies(monkeypatch, dummy_chat, dummy_bot_response)

    result = create_chat_service(mock_db_session, user_id, message_request_multiple_files)

    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."

    (mock_create_chat, mock_save_user_messages, mock_build_prompt, mock_call_bot, mock_add_message) = mocks
    mock_create_chat.assert_called_once_with(mock_db_session, user_id, "Chat Title")
    mock_save_user_messages.assert_called_once_with(mock_db_session, dummy_chat.id, message_request_multiple_files)
    mock_build_prompt.assert_called_once_with(mock_db_session, dummy_chat.id)
    mock_call_bot.assert_called_once_with("Prompt for bot")
    mock_add_message.assert_called_once_with(mock_db_session, dummy_chat.id, "bot", dummy_bot_response.text)


def test_service_chat_create_chat_multiple_files(mock_db_session, message_request_multiple_files, monkeypatch):
    """
    Unit test for successful execution of create_chat_service.

    User request text and multiple docx/pdf files
    """
    # Arrange
    user_id = uuid4()
    dummy_chat = MagicMock(id=1)
    dummy_bot_response = MessageResponse(id=1, chat_id=1, sender="bot", text="Bot responded.")

    # Patch the dependent functions to avoid hitting actual DB/bot
    monkeypatch.setattr("app.services.services_chat.create_chat", lambda db, uid, title: dummy_chat)
    monkeypatch.setattr("app.services.services_chat.save_user_messages", lambda db, chat_id, msg_in: None)
    monkeypatch.setattr("app.services.services_chat.build_prompt", lambda db, chat_id: "Prompt for bot")
    monkeypatch.setattr("app.services.services_chat.call_bot", lambda prompt: dummy_bot_response)
    monkeypatch.setattr("app.services.services_chat.add_message", lambda db, chat_id, sender, text: None)

    # Act
    result = create_chat_service(mock_db_session, user_id, message_request_multiple_files)

    # Assert
    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."


def test_service_chat_create_chat_raise_user_not_found(mock_db_session, message_request_multiple_files, monkeypatch):
    """
    Unit test for create_chat_service when user is not found.
    """
    # Arrange: generate a dummy user ID to simulate a real user
    user_id = uuid4()

    # Arrange: patch create_chat to raise UserNotFoundError
    mock_create_chat = MagicMock(side_effect=UserNotFoundError("User does not exist"))
    monkeypatch.setattr("app.services.services_chat.create_chat", mock_create_chat)

    # Act + Assert: verify NotFoundError is raised with the expected message
    with pytest.raises(NotFoundError, match="User not found"):
        create_chat_service(mock_db_session, user_id, message_request_multiple_files)

    # Extra Assert: confirm create_chat was actually called once with expected args
    mock_create_chat.assert_called_once_with(mock_db_session, user_id, "Chat Title") 


def test_service_chat_create_chat_raise_chat_not_found(mock_db_session, message_request_multiple_files, monkeypatch):
    """
    Unit test for create_chat_service: if add_message raises ChatNotFoundError,
    the service should raise NotFoundError after completing previous steps. 
    """
    # Arrange: generate a dummy user ID to simulate a real user
    user_id = uuid4()

    # Arrange: patch create_chat to raise ChatNotFoundError
    mock_create_chat = MagicMock(side_effect=ChatNotFoundError("Chat does not exist"))
    monkeypatch.setattr("app.services.services_chat.create_chat", mock_create_chat)

    # Act + Assert: verify NotFoundError is raised with the expected message
    with pytest.raises(NotFoundError, match="Chat not found"):
        create_chat_service(mock_db_session, user_id, message_request_multiple_files)

    # Extra Assert: confirm create_chat was actually called once with expected args
    mock_create_chat.assert_called_once_with(mock_db_session, user_id, "Chat Title")  