from io import BytesIO
from pdfminer.high_level import extract_text as extract_pdf_text
import docx
from app.schemas.schema_message import MessageRequest

def parse_pdf_bytes(file_bytes: bytes) -> MessageRequest:
    """Extract text from a PDF file given as bytes."""
    return MessageRequest(text= extract_pdf_text(BytesIO(file_bytes)))

def parse_docx_bytes(file_bytes: bytes) -> MessageRequest:
    """Extract text from a DOCX file given as bytes."""
    doc = docx.Document(BytesIO(file_bytes))
    return MessageRequest(text="\n".join([p.text for p in doc.paragraphs]))