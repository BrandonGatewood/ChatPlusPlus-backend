import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from io import BytesIO
from fastapi import UploadFile
from app.schemas.schema_message import MessageRequest
from app.services.services_shared import save_user_messages


@pytest.fixture
def mock_db_session():
    """Mock DB session fixture with context manager support."""
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db


def test_save_user_messages_no_files(mock_db_session, monkeypatch):
    """
    Unit test for save_user_messages with text only (no files).
    Should call add_message once with the text.
    """
    chat_id = uuid4()
    message_text = "Hello, this is a test."
    msg_in = MessageRequest(text=message_text, files=[])

    mock_add_message = MagicMock()
    monkeypatch.setattr("app.services.services_shared.add_message", mock_add_message)

    save_user_messages(mock_db_session, chat_id, msg_in)

    mock_add_message.assert_called_once_with(mock_db_session, chat_id, "user", message_text)


def test_save_user_messages_with_files(mock_db_session, monkeypatch):
    """
    Unit test for save_user_messages with text and files.
    Should call add_message once for text, then for each parsed file.
    """
    chat_id = uuid4()
    message_text = "Hello with files"
    files = [
        UploadFile(filename="dummy1.pdf", file=BytesIO(b"dummy content")),
        UploadFile(filename="dummy2.docx", file=BytesIO(b"dummy content")),
    ]
    msg_in = MessageRequest(text=message_text, files=files)

    # Mocks
    mock_add_message = MagicMock()
    monkeypatch.setattr("app.services.services_shared.add_message", mock_add_message)

    mock_parse_file = MagicMock(side_effect=["Parsed text 1", "Parsed text 2"])
    monkeypatch.setattr("app.services.services_shared.parse_file", mock_parse_file)

    save_user_messages(mock_db_session, chat_id, msg_in)

    # Assert text message saved first
    mock_add_message.assert_any_call(mock_db_session, chat_id, "user", message_text)

    # Assert parse_file called on each file
    assert mock_parse_file.call_count == len(files)
    for file in files:
        mock_parse_file.assert_any_call(file)

    # Assert add_message called with parsed text
    mock_add_message.assert_any_call(mock_db_session, chat_id, "user", "Parsed text 1")
    mock_add_message.assert_any_call(mock_db_session, chat_id, "user", "Parsed text 2")

    # Total expected add_message calls: 1 (text) + 2 (files) = 3
    assert mock_add_message.call_count == 3