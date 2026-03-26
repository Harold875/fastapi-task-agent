from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.models import Base

from app.config import settings

URL = settings.DATABASE_URL
engine = create_engine(URL, echo=True)
SessionDefault = sessionmaker(engine, expire_on_commit=False)


def init_db():
    with engine.begin() as conn:
        Base.metadata.create_all(conn)


def get_db():
    with SessionDefault() as session:
        yield session