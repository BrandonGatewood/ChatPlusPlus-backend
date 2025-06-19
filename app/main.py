from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.models.base import Base
from app.db.session import engine
from app.api.routes import auth 
from app.api.routes import user
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router with prefix /auth
app.include_router(auth.router, tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])