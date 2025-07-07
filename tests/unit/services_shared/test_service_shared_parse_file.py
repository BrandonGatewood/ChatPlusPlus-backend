import pytest
from io import BytesIO
from fastapi import UploadFile
from unittest.mock import MagicMock
from app.services.services_shared import parse_file
from app.exceptions import ExtensionsError


def test_parse_file_pdf_success(monkeypatch):
    """
    Test parse_file returns parsed text for PDF files.
    """
    # Arrange: PDF file with content
    dummy_bytes = b"pdf content"
    upload_file = UploadFile(filename="test.pdf", file=BytesIO(dummy_bytes))

    # Patch parse_pdf_bytes to return dummy parsed text
    mock_parse_pdf = MagicMock(return_value="Parsed PDF Text")
    monkeypatch.setattr("app.services.services_shared.parse_pdf_bytes", mock_parse_pdf)

    result = parse_file(upload_file)

    # Assert parse_pdf_bytes was called with correct bytes
    mock_parse_pdf.assert_called_once_with(dummy_bytes)
    assert result == "Parsed PDF Text"


def test_parse_file_docx_success(monkeypatch):
    """
    Test parse_file returns parsed text for DOCX files.
    """
    dummy_bytes = b"docx content"
    upload_file = UploadFile(filename="test.docx", file=BytesIO(dummy_bytes))

    # Patch parse_docx_bytes to return dummy parsed text
    mock_parse_docx = MagicMock(return_value="Parsed DOCX Text")
    monkeypatch.setattr("app.services.services_shared.parse_docx_bytes", mock_parse_docx)

    result = parse_file(upload_file)

    mock_parse_docx.assert_called_once_with(dummy_bytes)
    assert result == "Parsed DOCX Text"


def test_parse_file_unsupported_extension():
    """
    Test parse_file raises ExtensionsError on unsupported file types.
    """
    upload_file = UploadFile(filename="test.txt", file=BytesIO(b"some content"))

    with pytest.raises(ExtensionsError, match="Unsupported file type"):
        parse_file(upload_file)


def test_parse_file_empty_file():
    """
    Test parse_file raises ExtensionsError on empty file content.
    """
    upload_file = UploadFile(filename="test.pdf", file=BytesIO(b""))

    with pytest.raises(ExtensionsError, match="empty or could not be read"):
        parse_file(upload_file)