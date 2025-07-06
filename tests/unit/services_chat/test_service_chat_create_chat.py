from fastapi import UploadFile
import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from io import BytesIO
from app.exceptions import ChatNotFoundError, NotFoundError, UserNotFoundError
from app.services.services_chat import create_chat_service
from app.schemas.schema_message import MessageRequest, MessageResponse

@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session with context manager support."""
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db


### Fixtures for different request payload
@pytest.fixture
def message_request_empty_files():
    """Sample message request payload."""
    return MessageRequest(
        text="Hello, this is a test message.",
        files=[]
    )

@pytest.fixture
def message_request_one_pdf_file():
    """Sample message request payload."""
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
    """Sample message request payload."""
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
def message_request_multiple_files():
    """Sample message request payload."""
    return MessageRequest(
        text="Hello, this is a test message.",
        files=[
            UploadFile(
                filename="dummy.pdf",
                file=BytesIO(b"dummy content")
            ),
            UploadFile(
                filename="dummy.pdf",
                file=BytesIO(b"dummy content")
            ),
            UploadFile(
                filename="dummy.docx",
                file=BytesIO(b"dummy content")
            )
        ]
    )

def test_service_chat_create_chat_empty_files(mock_db_session, message_request_empty_files, monkeypatch):
    """
    Unit test for successful execution of create_chat_service.

    User request text and no files
    """

    # Arrange
    dummy_chat = MagicMock(id=1)
    dummy_bot_response = MessageResponse(id=1, chat_id=1, sender="bot", text="Hi from bot")

    # Patch the dependent functions to avoid hitting actual DB/bot
    monkeypatch.setattr("app.services.services_chat.create_chat", lambda db, uid, title: dummy_chat)
    monkeypatch.setattr("app.services.services_shared.save_user_messages", lambda db, chat_id, msg_in: None)
    monkeypatch.setattr("app.services.services_shared.build_prompt", lambda db, chat_id: "Prompt for bot")
    monkeypatch.setattr("app.services.services_shared.call_bot", lambda prompt: dummy_bot_response)
    monkeypatch.setattr("app.services.services_message.add_message", lambda db, chat_id, sender, text: None)

    user_id = uuid4()

    # Act
    result = create_chat_service(mock_db_session, user_id, message_request_empty_files)

    # Assert
    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."

def test_service_chat_create_chat_one_pdf_file(mock_db_session, message_request_one_pdf_file, monkeypatch):
    """
    Unit test for successful execution of create_chat_service.

    User request text and one pdf file 
    """

    # Arrange
    dummy_chat = MagicMock(id=1)
    dummy_bot_response = MessageResponse(id=1, chat_id=1, sender="bot", text="Hi from bot")

    # Patch the dependent functions to avoid hitting actual DB/bot
    monkeypatch.setattr("app.services.services_chat.create_chat", lambda db, uid, title: dummy_chat)
    monkeypatch.setattr("app.services.services_shared.save_user_messages", lambda db, chat_id, msg_in: None)
    monkeypatch.setattr("app.services.services_shared.build_prompt", lambda db, chat_id: "Prompt for bot")
    monkeypatch.setattr("app.services.services_shared.call_bot", lambda prompt: dummy_bot_response)
    monkeypatch.setattr("app.services.services_message.add_message", lambda db, chat_id, sender, text: None)
    monkeypatch.setattr("app.services.services_shared.parse_file", lambda file_bytes: "Parsed dummy text")

    user_id = uuid4()

    # Act
    result = create_chat_service(mock_db_session, user_id, message_request_one_pdf_file)

    # Assert
    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."

def test_service_chat_create_chat_one_docx_file(mock_db_session, message_request_one_docx_file, monkeypatch):
    """
    Unit test for successful execution of create_chat_service.
    
    User request text and one docx file 
    """

    # Arrange
    dummy_chat = MagicMock(id=1)
    dummy_bot_response = MessageResponse(id=1, chat_id=1, sender="bot", text="Hi from bot")

    # Patch the dependent functions to avoid hitting actual DB/bot
    monkeypatch.setattr("app.services.services_chat.create_chat", lambda db, uid, title: dummy_chat)
    monkeypatch.setattr("app.services.services_shared.save_user_messages", lambda db, chat_id, msg_in: None)
    monkeypatch.setattr("app.services.services_shared.build_prompt", lambda db, chat_id: "Prompt for bot")
    monkeypatch.setattr("app.services.services_shared.call_bot", lambda prompt: dummy_bot_response)
    monkeypatch.setattr("app.services.services_message.add_message", lambda db, chat_id, sender, text: None)
    monkeypatch.setattr("app.services.services_shared.parse_file", lambda file_bytes: "Parsed dummy text")

    user_id = uuid4()

    # Act
    result = create_chat_service(mock_db_session, user_id, message_request_one_docx_file)

    # Assert
    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."

def test_service_chat_create_chat_multiple_files(mock_db_session, message_request_multiple_files, monkeypatch):
    """
    Unit test for successful execution of create_chat_service.

    User request text and multiple docx/pdf files
    """

    # Arrange
    dummy_chat = MagicMock(id=1)
    dummy_bot_response = MessageResponse(id=1, chat_id=1, sender="bot", text="Hi from bot")

    # Patch the dependent functions to avoid hitting actual DB/bot
    monkeypatch.setattr("app.services.services_chat.create_chat", lambda db, uid, title: dummy_chat)
    monkeypatch.setattr("app.services.services_shared.save_user_messages", lambda db, chat_id, msg_in: None)
    monkeypatch.setattr("app.services.services_shared.build_prompt", lambda db, chat_id: "Prompt for bot")
    monkeypatch.setattr("app.services.services_shared.call_bot", lambda prompt: dummy_bot_response)
    monkeypatch.setattr("app.services.services_message.add_message", lambda db, chat_id, sender, text: None)
    monkeypatch.setattr("app.services.services_shared.parse_file", lambda file_bytes: "Parsed dummy text")

    user_id = uuid4()

    # Act
    result = create_chat_service(mock_db_session, user_id, message_request_multiple_files)

    # Assert
    assert isinstance(result, MessageResponse)
    assert result.text == "Bot responded."

def test_service_chat_create_chat_raise_user_not_found(mock_db_session, message_request_multiple_files, monkeypatch):
    """
    Unit test for create_chat_service when user is not found.
    """

    # Arrange: Patch create_chat to simulate user not found
    monkeypatch.setattr(
        "app.services.services_chat.create_chat",
        lambda db, uid, title: (_ for _ in ()).throw(UserNotFoundError("User not found"))
    )

    user_id = uuid4()

    # Act + Assert: Verify the expected exception is raised
    with pytest.raises(NotFoundError, match="User not found"):
        create_chat_service(mock_db_session, user_id, message_request_multiple_files) 

def test_service_chat_create_chat_raise_chat_not_found(mock_db_session, message_request_multiple_files, monkeypatch):
    """
    Unit test for create_chat_service when chat is not found.
    """

    # Arrange: Patch create_chat to simulate chat not found
    monkeypatch.setattr(
        "app.services.services_chat.create_chat",
        lambda db, uid, title: (_ for _ in ()).throw(ChatNotFoundError("Chat not found"))
    )

    user_id = uuid4()

    # Act + Assert: Verify the expected exception is raised
    with pytest.raises(NotFoundError, match="Chat not found"):
        create_chat_service(mock_db_session, user_id, message_request_multiple_files)
 