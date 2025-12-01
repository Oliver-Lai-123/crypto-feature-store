import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# You can later move this to env vars or a config module
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:12345678@host.docker.internal:5432/crypto_feature_store"
,
)

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    future=True,
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_session():
    """
    Helper for scripts (ingestion, transforms).
    Use like:

        from crypto_feature_store.db.session import get_session
        session = get_session()
    """
    return SessionLocal()


def get_db():
    """
    FastAPI dependency.
    Use in endpoints as: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
