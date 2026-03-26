from datetime import datetime, timezone
from enum import Enum
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, func


class Base(DeclarativeBase):
    pass


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus(Enum):
    PENDING = "pendiente"
    IN_PROGRESS = "en progreso"
    COMPLETED = "completada"


class TaskPriority(Enum):
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"


class Task(Base):
    __tablename__ = "task"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None]
    status: Mapped[TaskStatus]
    priority: Mapped[TaskPriority]
    due_date: Mapped[datetime] = mapped_column(default=get_datetime_utc)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=get_datetime_utc)
