from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import SessionDB
from app.models import Task, TaskStatus, TaskPriority
from app.schema import TaskBase, TaskPublic

router = APIRouter(prefix='/tasks', tags=['tasks'])

date_format = Annotated[date, Query(example="2026-03-27")]

@router.get('/')
async def get_all_tasks(
    session: SessionDB,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    created_at_from: date_format | None = None,
    created_at_to: date_format | None = None,
    due_date_from: date_format | None = None,
    due_date_to: date_format | None = None,
    limit: int = 100
) -> list[TaskPublic]:
    
    stmt = select(Task).limit(limit)
    if status:
        stmt = stmt.where(Task.status == status.name)
    if priority:
        stmt = stmt.where(Task.priority == priority.name)
    
    
    # filter date
    if created_at_from:
        stmt = stmt.where(Task.created_at >= created_at_from)

    if created_at_to:
        stmt = stmt.where(Task.created_at <= created_at_to)
    
    if due_date_from:
        stmt = stmt.where(Task.due_date >= due_date_from)
    
    if due_date_to:
        stmt = stmt.where(Task.due_date <= due_date_to)


    tasks = session.scalars(stmt).all()
    return tasks


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_task(session: SessionDB, task: TaskBase) -> TaskPublic:
    try:
        t = Task(**task.model_dump())
        session.add(t)
        session.commit()
        return t
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.get('/{id}')
async def get_one_task(session: SessionDB, id: int) -> TaskPublic:
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put('/{id}')
async def update_task(session: SessionDB, id: int, task_in: TaskBase) -> TaskPublic:
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task_in.model_dump().items():
        setattr(task, key, value)
    
    session.commit()
    return task


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(session: SessionDB, id: int) -> None:
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit() 
    return