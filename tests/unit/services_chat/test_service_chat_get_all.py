import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from app.services.services_chat import get_all_chat_titles_service
from app.schemas.schema_chat import ChatTitle


@pytest.fixture
def mock_db_session():
    """Returns a mock SQLAlchemy session with context manager support."""
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    return db


def test_service_chat_get_all_chat_returns_list(mock_db_session, monkeypatch):
    """
    Unit test for successful execution of get_all_chat_titles_service.
    """
    # Arrange: generate to simulate a real data 
    user_id = uuid4()
    dummy_chat_titles = [
        ChatTitle(id=uuid4(), title="Chat One"),
        ChatTitle(id=uuid4(), title="Chat Two"),
    ]

    # Patch get_all_chat_titles with MagicMock returning dummy list
    mock_get_all_chat_titles = MagicMock(return_value=dummy_chat_titles)
    monkeypatch.setattr("app.services.services_chat.get_all_chat_titles", mock_get_all_chat_titles)

    # Act
    result = get_all_chat_titles_service(mock_db_session, user_id)

    # Assert results are correct
    assert isinstance(result, list)
    assert all(isinstance(chat, ChatTitle) for chat in result)
    assert len(result) == 2
    assert result[0].title == "Chat One"
    assert result[1].title == "Chat Two"

    # Assert get_all_chat_titles was called once with correct args
    mock_get_all_chat_titles.assert_called_once_with(mock_db_session, user_id) 