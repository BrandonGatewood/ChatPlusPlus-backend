from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.llm import generate_llm_response
from app.core.auth import get_current_user
from app.db.session import get_db
from app.db.models.user import User
import pdfplumber
import io
from docx import Document

router = APIRouter()

class ChatRequest(BaseModel):
    job_description: str
    current_resume: str
    user_message: str

@router.post("/chat")
def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prompt = (
        f"You are a professional resume editor.\n"
        f"Given the job description:\n{request.job_description}\n\n"
        f"and the current resume draft:\n{request.current_resume}\n\n"
        f"The user says: {request.user_message}\n\n"
        f"Reply with the updated resume or specific edits."
    )

    try:
        response_text = generate_llm_response(prompt)
        return {"llm_reply": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation error: {e}")

@router.post("/upload-resume")
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contents = file.file.read()
    file_name = file.filename.lower()

    try:
        if file_name.endswith(".pdf"):
            text = extract_text_from_pdf(contents)
        elif file_name.endswith(".docx"):
            text = extract_text_from_docx(contents)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF or DOCX.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {e}")

    return {"resume_text": text}

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    return text.strip()

def extract_text_from_docx(docx_bytes: bytes) -> str:
    doc = Document(io.BytesIO(docx_bytes))
    return "\n".join(para.text for para in doc.paragraphs).strip()