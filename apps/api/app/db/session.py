from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base

engine = create_engine(settings.database_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    from app.models.assessment import Assessment, AssessmentResult, IngestionJob, ReportArtifact, StandardDocument, User  # noqa: F401
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        existing = db.query(User).filter(User.email == settings.bootstrap_admin_email).first()
        if not existing:
            db.add(
                User(
                    email=settings.bootstrap_admin_email,
                    full_name='Bootstrap Admin',
                    password_hash=get_password_hash(settings.bootstrap_admin_password),
                    role='admin',
                    is_active=True,
                )
            )
            db.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
