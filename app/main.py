from fastapi import FastAPI
from app.api.routes import auth  # import your auth routes

app = FastAPI()

# Include auth router with prefix /auth
app.include_router(auth.router, prefix="/auth", tags=["auth"])