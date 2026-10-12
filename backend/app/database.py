from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Local SQLite file next to the backend folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./flashdeck.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_audit_columns():
    """Add created_at, updated_at, and is_deleted to tables created before those columns existed."""
    inspector = inspect(engine)
    existing = set(inspector.get_table_names())
    with engine.begin() as conn:
        for table in ("courses", "flashcards"):
            if table not in existing:
                continue
            cols = {column["name"] for column in inspector.get_columns(table)}
            if "created_at" not in cols:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN created_at DATETIME"))
            if "updated_at" not in cols:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN updated_at DATETIME"))
            if "is_deleted" not in cols:
                conn.execute(text(
                    f"ALTER TABLE {table} ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT 0"
                ))
            if table == "flashcards" and "is_approved" not in cols:
                conn.execute(text(
                    "ALTER TABLE flashcards ADD COLUMN is_approved BOOLEAN NOT NULL DEFAULT 1"
                ))
            conn.execute(text(
                f"UPDATE {table} SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"
            ))
            conn.execute(text(
                f"UPDATE {table} SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"
            ))


def get_db():
    """Dependency: yield a DB session, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
