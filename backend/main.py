"""
FlashDeck backend entrypoint.
MVC-style API (Model + Controller). No server-rendered views.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine, ensure_audit_columns
from app.controllers import course_controller, friend_controller, user_controller
from app.models import course as course_model  # noqa: F401
from app.models import flashcard as flashcard_model  # noqa: F401
from app.models import friend_request as friend_request_model  # noqa: F401
from app.services import course_service, friend_service

# Create SQLite tables on startup, then fill in columns on tables that already existed
Base.metadata.create_all(bind=engine)
ensure_audit_columns()

db = SessionLocal()
try:
    course_service.seed_demo(db)
    friend_service.seed_demo_friend(db)
finally:
    db.close()

app = FastAPI(title="FlashDeck API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_controller.router, prefix="/api")
app.include_router(course_controller.router, prefix="/api")
app.include_router(friend_controller.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "FlashDeck API is running"}
