from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.db.base import Base


# Optimize SQLite for better performance
sqlite_connect_args = {}
if settings.db_url.startswith("sqlite"):
    sqlite_connect_args = {
        "check_same_thread": False,
        "timeout": 30,  # Increase timeout for concurrent operations
    }
    # Enable WAL mode and other optimizations via PRAGMA
    # These will be set on connection

engine = create_engine(
    settings.db_url, 
    connect_args=sqlite_connect_args,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Disable SQL logging for performance
)

# Set SQLite optimizations on engine creation
if settings.db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Set SQLite PRAGMA settings for better performance."""
        cursor = dbapi_conn.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and speed
            cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
            cursor.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
        finally:
            cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


