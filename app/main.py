from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.models.base import Base
from app.db.session import engine
from app.api.routes import auth 
from app.api.routes import chat
from app.api.routes import message
from app.api.routes import websocket

from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv("FRONTEND_URL")
if url.endswith("/"):
    url = url[:-1]

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[url], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router with prefix /auth
app.include_router(auth.router, tags=["auth"])
app.include_router(chat.router, tags=["chat"])
app.include_router(message.router, tags=["message"])
app.include_router(websocket.router, tags=["websocket"])
