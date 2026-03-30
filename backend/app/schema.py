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


class TaskSummary(BaseModel):
    total_tasks: int
    distribution_by_status: dict[TaskStatus, int]
    distribution_by_priority: dict[TaskPriority, int]
    tasks_overdue: int
    tasks_due_soon: int
    message: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_tasks": 6,
                    "distribution_by_status": {i.value: 1 for i in TaskStatus},
                    "distribution_by_priority": {i.value: 1 for i in TaskPriority},
                    "tasks_overdue": 1,
                    "tasks_due_soon": 2,
                    "message": "string",
                },
            ]
        }
    }
