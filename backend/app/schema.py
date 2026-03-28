from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from app.models import TaskStatus, TaskPriority, get_datetime_utc


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.LOW)
    due_date: datetime = Field(
        default=(get_datetime_utc() + timedelta(days=1)))


class TaskPublic(TaskBase):
    id: int
    created_at: datetime
    last_updated: datetime


class TaskUpdate(TaskBase):
    title: str | None = None
