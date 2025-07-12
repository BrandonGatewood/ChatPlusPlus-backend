import pytest
from uuid import uuid4
from io import BytesIO
from unittest.mock import MagicMock
from fastapi import UploadFile
from app.exceptions import ChatNotFoundError, NotFoundError, UserNotFoundError
from app.schemas.schema_chat import ChatTitle
from app.schemas.schema_message import MessageRequest
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


def patch_create_chat_dependencies(monkeypatch, dummy_chat):
    """
    Helper: patch all functions called by create_chat_service using MagicMock,
    so they can be asserted later if needed.
    """
    mock_create_chat = MagicMock(return_value=dummy_chat)
    mock_save_user_messages = MagicMock()

    monkeypatch.setattr("app.services.services_chat.create_chat", mock_create_chat)
    monkeypatch.setattr("app.services.services_chat.save_user_messages", mock_save_user_messages)

    return (
        mock_create_chat,
        mock_save_user_messages,
    )


def test_service_chat_create_chat_empty_files(mock_db_session, message_request_empty_files, monkeypatch):
    """
    Unit test for create_chat_service with user text and no files.
    """
    user_id = uuid4()
    dummy_chat = ChatTitle(id=uuid4(), title="Chat Title")

    # Arrange
    mocks = patch_create_chat_dependencies(monkeypatch, dummy_chat)

    # Act
    result = create_chat_service(mock_db_session, user_id, message_request_empty_files)

    # Assert: result correctness
    assert isinstance(result, ChatTitle)
    assert result.id == dummy_chat.id
    assert result.title == dummy_chat.title

    # Assert: verify calls
    (mock_create_chat, mock_save_user_messages) = mocks
    mock_create_chat.assert_called_once_with(mock_db_session, user_id, dummy_chat.title)
    mock_save_user_messages.assert_called_once_with(mock_db_session, dummy_chat.id, message_request_empty_files)


def test_service_chat_create_chat_one_pdf_file(mock_db_session, message_request_one_pdf_file, monkeypatch):
    """
    Unit test for create_chat_service with user text and one PDF file.
    """
    user_id = uuid4()
    dummy_chat = ChatTitle(id=uuid4(), title="Chat Title")

    mocks = patch_create_chat_dependencies(monkeypatch, dummy_chat)

    result = create_chat_service(mock_db_session, user_id, message_request_one_pdf_file)

    assert isinstance(result, ChatTitle)
    assert result.id == dummy_chat.id
    assert result.title == dummy_chat.title

    (mock_create_chat, mock_save_user_messages) = mocks
    mock_create_chat.assert_called_once_with(mock_db_session, user_id, dummy_chat.title)
    mock_save_user_messages.assert_called_once_with(mock_db_session, dummy_chat.id, message_request_one_pdf_file)
    


def test_service_chat_create_chat_one_docx_file(mock_db_session, message_request_one_docx_file, monkeypatch):
    """
    Unit test for create_chat_service with user text and one DOCX file.
    """
    user_id = uuid4()
    dummy_chat = ChatTitle(id=uuid4(), title="Chat Title")

    mocks = patch_create_chat_dependencies(monkeypatch, dummy_chat)

    result = create_chat_service(mock_db_session, user_id, message_request_one_docx_file)

    assert isinstance(result, ChatTitle)
    assert result.id == dummy_chat.id
    assert result.title == dummy_chat.title

    (mock_create_chat, mock_save_user_messages) = mocks
    mock_create_chat.assert_called_once_with(mock_db_session, user_id, dummy_chat.title)
    mock_save_user_messages.assert_called_once_with(mock_db_session, dummy_chat.id, message_request_one_docx_file)


def test_service_chat_create_chat_multiple_files(mock_db_session, message_request_multiple_files, monkeypatch):
    """
    Unit test for create_chat_service with user text and multiple PDF/DOCX files.
    """
    user_id = uuid4()
    dummy_chat = ChatTitle(id=uuid4(), title="Chat Title")

    mocks = patch_create_chat_dependencies(monkeypatch, dummy_chat)

    result = create_chat_service(mock_db_session, user_id, message_request_multiple_files)

    assert isinstance(result, ChatTitle)
    assert result.id == dummy_chat.id
    assert result.title == dummy_chat.title

    (mock_create_chat, mock_save_user_messages) = mocks
    mock_create_chat.assert_called_once_with(mock_db_session, user_id, dummy_chat.title)
    mock_save_user_messages.assert_called_once_with(mock_db_session, dummy_chat.id, message_request_multiple_files)
    

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