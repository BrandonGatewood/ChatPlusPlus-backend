from io import BytesIO
from pdfminer.high_level import extract_text as extract_pdf_text
import docx


def parse_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file given as bytes.

    Args:
        file_bytes: The binary contents of a PDF file

    Returns:
        The extracted file as string
    """
    return extract_pdf_text(BytesIO(file_bytes))


def parse_docx_bytes(file_bytes: bytes) -> str:
    """
    Extract text from a DOCX file given as bytes.
    
    Args:
        file_bytes: The binary contents of a Docx file

    Returns:
        The extracted file as string
    """
    doc = docx.Document(BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs])